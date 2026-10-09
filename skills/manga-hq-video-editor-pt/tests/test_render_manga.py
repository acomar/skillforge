import copy
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
import wave
import zlib

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "render_manga.py"
spec = importlib.util.spec_from_file_location("render_manga", MODULE)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


def png(path, width, height, tint=255):
    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind+payload)&0xffffffff)
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            ink = x < 8 or y < 8 or x >= width-8 or y >= height-8
            ink = ink or (height//3 < y < height//3+10 and width//5 < x < width*4//5)
            value = 8 if ink else tint
            raw.extend((value, value, value, 255))
    data = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw))) + chunk(b"IEND", b""))
    path.write_bytes(data)


def audio(path, hz):
    with wave.open(str(path), "wb") as target:
        target.setnchannels(1)
        target.setsampwidth(2)
        target.setframerate(48000)
        target.writeframes(b"".join(struct.pack("<h", round(5000*math.sin(2*math.pi*hz*i/48000)))
                                  for i in range(48000*6)))


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg/FFprobe required")
class RendererTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_root = Path(os.environ.get("MANGA_RENDER_TEST_ROOT", str(Path.cwd()/"work"/"render-tests")))
        test_root.mkdir(parents=True,exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(prefix="manga-render-tests-",dir=test_root)
        cls.root = Path(cls.temp.name) / "pasta com ação 漫画"
        cls.root.mkdir()
        cls.image1 = cls.root / "página ação.png"
        cls.image2 = cls.root / "quadro 漫画.png"
        png(cls.image1, 220, 300)
        png(cls.image2, 360, 220)
        audio(cls.root / "grave.wav", 440)
        audio(cls.root / "agudo.wav", 880)
        subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-v", "error", "-i", str(cls.root/"grave.wav"),
                        "-i", str(cls.root/"agudo.wav"), "-map", "0:a:0", "-map", "1:a:0", "-c:a", "flac",
                        str(cls.root/"faixas distintas.mka")], check=True, capture_output=True)
        cls.plan = {"schema_version": 1, "profile": renderer.PROFILE, "readiness": "ready", "renderable": True,
                    "canvas": {"width": 640, "height": 360, "fps": "15/1"},
                    "audio": {"file": "faixas distintas.mka", "stream_index": 1},
                    "beats": [{"id": "painel-1", "start": 0, "end": 3, "image": cls.image1.name,
                               "bbox": [.05,.05,.95,.95], "motion": {"from_scale": 1, "to_scale": 1.8},
                               "transition_seconds": .2, "legibility_reviewed": True},
                              {"id": "painel-2", "start": 3, "end": 6, "image": cls.image2.name,
                               "motion": {"from_scale": 1.8, "to_scale": 1}, "transition_seconds": .2,
                               "legibility_reviewed": True}]}
        cls.tools = renderer.tool_paths()

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def save(self, data, name="plan.json"):
        path = self.root/name
        path.write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")
        return path

    def reject(self, change, message):
        data = copy.deepcopy(self.plan)
        change(data)
        with self.assertRaisesRegex(renderer.RenderError, message):
            renderer.validate_plan(self.save(data),self.tools)

    def test_missing_stream_is_rejected(self):
        self.reject(lambda p:p["audio"].pop("stream_index"),"explicit")

    def test_boolean_schema_is_rejected(self):
        self.reject(lambda p:p.update(schema_version=True),"schema_version")

    def test_missing_master_readiness_is_rejected(self):
        self.reject(lambda p:p.pop("readiness"),"unconfirmed")

    def test_unknown_master_readiness_is_rejected(self):
        self.reject(lambda p:p.update(readiness="maybe"),"unconfirmed")

    def test_nonexistent_audio_stream_is_rejected(self):
        self.reject(lambda p:p["audio"].update(stream_index=8),"not an audio stream")

    def test_stale_reviewed_audio_hash_is_rejected(self):
        self.reject(lambda p:p["audio"].update(sha256="0"*64),"does not match the reviewed plan")

    def test_stale_reviewed_image_hash_is_rejected(self):
        self.reject(lambda p:p["beats"][0].update(image_sha256="0"*64),"does not match the reviewed plan")

    def test_original_background_outlines_are_white_without_channel_wrap(self):
        raw=subprocess.run(["ffmpeg","-v","error","-filter_threads","1","-f","lavfi","-i",
                            renderer.background_filter(320,180,"1/1",.1,0),"-frames:v","1",
                            "-pix_fmt","rgb24","-f","rawvideo","-"],capture_output=True,check=True).stdout
        bright=[(r,g,b) for r,g,b in zip(raw[0::3],raw[1::3],raw[2::3]) if r>180 and g>180]
        self.assertGreater(len(bright),50)
        self.assertTrue(all(max(pixel)-min(pixel)<=3 for pixel in bright))

    def test_gap_over_frame_is_rejected(self):
        self.reject(lambda p:p["beats"][1].update(start=3.2),"gap/overlap")

    def test_overlap_over_frame_is_rejected(self):
        self.reject(lambda p:p["beats"][1].update(start=2.8),"gap/overlap")

    def test_audio_coverage_short_is_rejected(self):
        self.reject(lambda p:p["beats"][1].update(end=5.8),"audio duration")

    def test_bbox_xywh_mistake_is_rejected(self):
        self.reject(lambda p:p["beats"][0].update(bbox=[.6,.1,.2,.8]),"ordered normalized XYXY")

    def test_motion_nan_is_rejected(self):
        self.reject(lambda p:p["beats"][0]["motion"].update(to_scale=float("nan")),"finite")

    def test_unreviewed_image_is_rejected_for_master(self):
        self.reject(lambda p:p["beats"][0].update(legibility_reviewed=False),"legibility_reviewed")

    def test_draft_can_only_preview(self):
        data = copy.deepcopy(self.plan)
        data.update(readiness="draft",renderable=False)
        path = self.save(data)
        with self.assertRaisesRegex(renderer.RenderError,"Draft"):
            renderer.validate_plan(path,self.tools)
        validated = renderer.validate_plan(path,self.tools,preview=(320,180))
        self.assertTrue(validated["preview"])

    def test_sources_are_never_overwritten(self):
        path=self.save(self.plan)
        with self.assertRaisesRegex(renderer.RenderError,"new path"):
            renderer.render(path,self.image1,self.root/"bad-work",None,1,120,False)

    def test_six_second_render_selects_one_audio_and_resumes(self):
        path=self.save(self.plan,"pilot.json")
        work=self.root/"render work"
        first=renderer.render(path,self.root/"piloto ação.mp4",work,None,1,180,True)
        self.assertEqual(first["validation"]["video_frames"],90)
        self.assertEqual(first["validation"]["audio_streams"],1)
        self.assertTrue(first["validation"]["decoded"])
        self.assertEqual(first["rendered_segments"],2)
        report=json.loads(Path(first["report"]).read_text(encoding="utf-8"))
        measured=report["loudness"]["delivery_measurement"]
        self.assertLessEqual(float(measured["true_peak_dbtp"]),-.95)
        self.assertLess(abs(float(measured["integrated_lufs"])+17),1)
        # The selected second audio track is880Hz; global mux must not use440Hz
        # or create silence at the join between the two video-only segments.
        raw=subprocess.run(["ffmpeg","-v","error","-i",first["output"],"-map","0:a:0","-ac","1",
                            "-ar","48000","-f","s16le","-"],capture_output=True,check=True).stdout
        samples=struct.unpack("<"+"h"*(len(raw)//2),raw)
        section=samples[48000:48000*2]
        crossings=sum(a<=0<b for a,b in zip(section,section[1:]))
        self.assertLess(abs(crossings-880),4)
        join=samples[round(2.98*48000):round(3.02*48000)]
        self.assertGreater(sum(abs(v) for v in join)/len(join),100)
        # Verify visible cyan panel plus original blue background and actual
        # growth, not merely a technically valid all-black movie.
        def frame(time):
            return subprocess.run(["ffmpeg","-v","error","-ss",str(time),"-i",first["output"],
                                   "-frames:v","1","-pix_fmt","rgb24","-f","rawvideo","-"],
                                  capture_output=True,check=True).stdout
        early,later=frame(.5),frame(2.5)
        def cyan_count(data):
            return sum(30<r<120 and 120<g<220 and b>215 for r,g,b in zip(data[0::3],data[1::3],data[2::3]))
        self.assertGreater(cyan_count(early),1000)
        self.assertGreater(cyan_count(later),cyan_count(early)*1.3)
        self.assertGreater(early[2],early[0]+30)
        second=renderer.render(path,self.root/"piloto retomado.mp4",work,None,1,180,True)
        self.assertEqual(second["reused_segments"],2)
        self.assertEqual(second["validation"]["sha256"],first["validation"]["sha256"])
        # Byte change in one image invalidates only its segment, leaving the
        # other validated segment reusable despite a new project cache key.
        png(self.image1,220,300,tint=230)
        third=renderer.render(path,self.root/"piloto alterado.mp4",work,None,1,180,True)
        self.assertEqual(third["rendered_segments"],1)
        self.assertEqual(third["reused_segments"],1)
        self.assertNotEqual(third["validation"]["sha256"],first["validation"]["sha256"])
        png(self.image1,220,300)


if __name__=="__main__":
    unittest.main()
