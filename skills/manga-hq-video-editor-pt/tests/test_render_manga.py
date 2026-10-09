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
from unittest import mock
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
            value = (8, 8, 8) if ink else ((tint, tint, tint) if isinstance(tint, int) else tint)
            raw.extend((*value, 255))
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


def motion_markers(path):
    """Opaque colored markers on transparency make decoded camera drift measurable."""
    width, height = 1200, 720
    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind+payload)&0xffffffff)
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            marker = next((color for center, color in ((300,(255,0,0,255)), (600,(0,255,0,255)),
                                                       (900,(0,0,255,255)))
                           if center-10 <= x < center+10 and 330 <= y < 390), (0,0,0,0))
            raw.extend(marker)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(bytes(raw))) + chunk(b"IEND", b""))


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
        cls.background = cls.root / "ambiente original 漫画.png"
        png(cls.image1, 220, 300)
        png(cls.image2, 360, 220)
        png(cls.background, 640, 360, tint=(150, 90, 50))
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
                               "transition_seconds": .2, "legibility_reviewed": True, "color_mode": "manga_cyan"},
                              {"id": "painel-2", "start": 3, "end": 6, "image": cls.image2.name,
                               "motion": {"from_scale": 1.8, "to_scale": 1}, "transition_seconds": .2,
                               "legibility_reviewed": True, "color_mode": "manga_cyan"}]}
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

    def test_ambient_fallback_is_muted_and_has_no_bright_overlay(self):
        raw=subprocess.run(["ffmpeg","-v","error","-filter_threads","1","-f","lavfi","-i",
                            renderer.background_filter(320,180,"1/1",.1,0),"-frames:v","1",
                            "-pix_fmt","rgb24","-f","rawvideo","-"],capture_output=True,check=True).stdout
        self.assertEqual(len(raw),320*180*3)
        pixels=list(zip(raw[0::3],raw[1::3],raw[2::3]))
        self.assertLess(max(max(pixel) for pixel in pixels),60)
        self.assertGreater(max(max(pixel) for pixel in pixels)-min(min(pixel) for pixel in pixels),10)
        # No abrupt bright outlines or high-frequency geometry: neighboring
        # channel values change gently in the actual decoded fallback frame.
        self.assertLess(max(abs(raw[i]-raw[i+3]) for i in range(0,len(raw)-3) if i//960==(i+3)//960),5)

    def test_default_preserves_original_panel_color_and_accepts_legacy_profile(self):
        data=copy.deepcopy(self.plan)
        data["profile"]="manga-blue-longform-v1"
        for beat in data["beats"]:
            beat.pop("color_mode")
        validated=renderer.validate_plan(self.save(data),self.tools)
        self.assertTrue(all(beat["color_mode"]=="original" for beat in validated["beats"]))
        self.assertEqual(validated["background"]["mode"],"ambient")

    def test_missing_background_image_is_rejected(self):
        self.reject(lambda p:p.update(visual_identity={"background":{"mode":"image","file":"absent.png"}}),
                    "background.file does not exist")

    def test_stale_background_hash_is_rejected(self):
        self.reject(lambda p:p.update(visual_identity={"background":{"mode":"image","file":self.background.name,
                                                                   "sha256":"0"*64}}),"does not match the reviewed plan")

    def test_invalid_background_file_is_rejected(self):
        broken=self.root/"broken background.png"
        broken.write_text("not an image",encoding="utf-8")
        self.reject(lambda p:p.update(visual_identity={"background":{"mode":"image","file":broken.name}}),
                    "ffprobe exited|Invalid dimensions")

    def test_background_palette_darkness_and_motion_are_validated(self):
        self.reject(lambda p:p.update(visual_identity={"background":{"mode":"ambient","palette":["blue","black"]}}),
                    "two #RRGGBB")
        self.reject(lambda p:p.update(visual_identity={"background":{"mode":"ambient","darkness":.9}}),"0..0.65")
        self.reject(lambda p:p.update(visual_identity={"background":{"mode":"image","file":self.background.name,
                                                                   "zoom_to":1.8}}),"between 1 and 1.12")

    def test_custom_ambient_palette_is_visible_in_decoded_frame(self):
        source=renderer.background_filter(320,180,"1/1",.1,0,{"palette":["#361A16","#482722"],"darkness":0})
        raw=subprocess.run(["ffmpeg","-v","error","-filter_threads","1","-f","lavfi","-i",source,
                            "-frames:v","1","-pix_fmt","rgb24","-f","rawvideo","-"],
                           capture_output=True,check=True).stdout
        pixel=raw[(90*320+160)*3:(90*320+160)*3+3]
        self.assertGreater(pixel[0],pixel[1]+20)
        self.assertGreater(pixel[1],pixel[2])

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

    def test_motion_easing_is_validated_and_defaults_to_smoothstep(self):
        data = copy.deepcopy(self.plan)
        data["beats"][0].pop("transition_seconds")
        data["beats"][1]["motion"]["easing"] = "linear"
        validated = renderer.validate_plan(self.save(data), self.tools)
        self.assertEqual(validated["beats"][0]["motion"]["easing"], "smoothstep")
        self.assertEqual(validated["beats"][1]["motion"]["easing"], "linear")
        self.assertEqual(validated["beats"][0]["transition_seconds"], .25)
        self.assertEqual(validated["beats"][1]["transition_seconds"], .2)
        for invalid in ("bounce", True, None, []):
            self.reject(lambda p:p["beats"][0]["motion"].update(easing=invalid), "smoothstep or linear")

    def test_motion_working_grid_is_bounded_and_reported(self):
        for dimensions, expected in (((960,540),4), ((1920,1080),2), ((1080,1920),2),
                                     ((3840,2160),1), ((7680,4320),1)):
            self.assertEqual(renderer.motion_supersampling(*dimensions), expected)
        validated = renderer.validate_plan(self.save(self.plan), self.tools, preview=(960,540))
        self.assertEqual(validated["motion_rendering"]["input_supersampling"],4)
        self.assertEqual(validated["renderer_version"], "1.2.0")

    def test_unplanned_motion_uses_snapped_duration_and_alternates_without_retiming(self):
        data=copy.deepcopy(self.plan)
        data["beats"][0]["end"]=1.03
        data["beats"][1]["start"]=1.03
        for beat in data["beats"]:
            beat.pop("motion")
        validated=renderer.validate_plan(self.save(data),self.tools)
        first,second=validated["beats"]
        self.assertEqual(first["motion"],{"from_scale":1,"to_scale":1.25,"easing":"smoothstep"})
        self.assertEqual(second["motion"],{"from_scale":1.3,"to_scale":1,"easing":"smoothstep"})
        self.assertEqual([first["frames"],second["frames"]],[15,75])
        self.assertEqual(validated["frames"],90)
        self.assertEqual(validated["duration"],6)
        self.assertEqual(validated["audio"]["stream_index"],1)
        self.assertEqual(validated["audio"]["sha256"],renderer.file_hash(self.root/"faixas distintas.mka"))
        # Partial objects have long supported independent endpoint defaults.
        # This correction must not silently reinterpret a reviewed endpoint.
        data["beats"][0]["motion"]={"from_scale":1.2}
        data["beats"][1]["motion"]={"to_scale":1.4}
        partial=renderer.validate_plan(self.save(data),self.tools)
        self.assertEqual(partial["beats"][0]["motion"]["to_scale"],1.8)
        self.assertEqual(partial["beats"][0]["motion"]["from_scale"],1.2)
        self.assertEqual(partial["beats"][1]["motion"]["from_scale"],1)
        self.assertEqual(partial["beats"][1]["motion"]["to_scale"],1.4)

    def motion_frames(self, path, beat, canvas):
        raw = subprocess.run(["ffmpeg","-v","error","-filter_threads","1","-i",str(path),
                              "-vf",renderer.panel_filter(beat,canvas),"-frames:v",str(beat["frames"]),
                              "-pix_fmt","rgba","-f","rawvideo","-"],capture_output=True,check=True).stdout
        frame_size = canvas["width"]*canvas["height"]*4
        self.assertEqual(len(raw),frame_size*beat["frames"])
        return [raw[index:index+frame_size] for index in range(0,len(raw),frame_size)]

    @staticmethod
    def marker_centroid(frame, width, channel):
        weight_sum = x_sum = y_sum = 0
        for pixel in range(len(frame)//4):
            rgba=frame[pixel*4:pixel*4+4]
            weight=max(0,rgba[channel]-max(rgba[(channel+1)%3],rgba[(channel+2)%3]))*rgba[3]
            weight_sum+=weight
            x_sum+=(pixel%width)*weight
            y_sum+=(pixel//width)*weight
        if not weight_sum:
            raise AssertionError("Rendered marker is missing")
        return x_sum/weight_sum, y_sum/weight_sum

    def test_decoded_zoom_is_smooth_monotonic_and_keeps_alpha_and_endpoints(self):
        image=self.root/"motion markers.png"
        motion_markers(image)
        canvas={"width":320,"height":180,"fps":"30/1"}
        beat={"crop":[0,0,1200,720],"frames":91,"start":0,"end":91/30,
              "motion":{"from_scale":1,"to_scale":1.45,"easing":"smoothstep"},
              "focal_point":[.5,.5],"transition_seconds":0,"color_mode":"original"}
        frames=self.motion_frames(image,beat,canvas)
        red=[self.marker_centroid(frame,320,0)[0] for frame in frames]
        green=[self.marker_centroid(frame,320,1) for frame in frames]
        self.assertLess(red[-1],red[0]-25)
        self.assertLess(max(point[0] for point in green)-min(point[0] for point in green),.5)
        self.assertLess(max(point[1] for point in green)-min(point[1] for point in green),.5)
        self.assertTrue(all(b-a<=.15 for a,b in zip(red,red[1:])))
        self.assertGreater(red[40]-red[50],4*(red[0]-red[10]))
        self.assertGreater(red[40]-red[50],4*(red[80]-red[90]))
        # Transparent surroundings survive camera resampling; no opaque black
        # canvas may replace the project's visible background.
        self.assertTrue(all(frame[3]==0 for frame in frames))
        self.assertGreater(sum(frames[45][index]>0 for index in range(3,len(frames[45]),4)),100)
        linear=copy.deepcopy(beat)
        linear["motion"]["easing"]="linear"
        linear_frames=self.motion_frames(image,linear,canvas)
        self.assertEqual(frames[0],linear_frames[0])
        self.assertEqual(frames[-1],linear_frames[-1])
        self.assertGreater(red[20]-self.marker_centroid(linear_frames[20],320,0)[0],2)
        reverse=copy.deepcopy(beat)
        reverse["motion"].update(from_scale=1.45,to_scale=1)
        reverse_frames=self.motion_frames(image,reverse,canvas)
        self.assertEqual(frames[-1],reverse_frames[0])
        self.assertEqual(frames[0],reverse_frames[-1])
        # A real coarse-canvas render exhibits the integer crop wobble this
        # change addresses. Oversampling must reduce measured center drift,
        # rather than merely producing a valid stream or a different filter.
        with mock.patch.object(renderer,"motion_supersampling",return_value=1):
            coarse=self.motion_frames(image,beat,canvas)
        coarse_green=[self.marker_centroid(frame,320,1) for frame in coarse]
        for axis in (0,1):
            fine_range=max(point[axis] for point in green)-min(point[axis] for point in green)
            coarse_range=max(point[axis] for point in coarse_green)-min(point[axis] for point in coarse_green)
            self.assertLess(fine_range,coarse_range/2)

    def test_image_background_zoom_is_continuous_across_cut(self):
        canvas={"width":320,"height":180,"fps":"30/1"}
        background={"mode":"image","zoom_from":1,"zoom_to":1.06,"darkness":0}
        def decode(start,count):
            beat={"start":start,"frames":count}
            raw=subprocess.run(["ffmpeg","-v","error","-filter_threads","1","-i",str(self.background),
                                "-vf",renderer.image_background_filter(background,canvas,beat,61),
                                "-frames:v",str(count),"-pix_fmt","rgba","-f","rawvideo","-"],
                               capture_output=True,check=True).stdout
            self.assertEqual(len(raw),count*320*180*4)
            return raw
        full=decode(0,61)
        split=decode(0,30)+decode(1,31)
        self.assertEqual(full,split)

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

    def test_background_image_is_a_protected_source(self):
        data=copy.deepcopy(self.plan)
        data["visual_identity"]={"background":{"mode":"image","file":self.background.name}}
        with self.assertRaisesRegex(renderer.RenderError,"new path"):
            renderer.render(self.save(data),self.background,self.root/"bad-background-work",None,1,120,False)

    def test_background_image_is_visible_and_changed_bytes_invalidate_all_segments(self):
        data=copy.deepcopy(self.plan)
        data["visual_identity"]={"name":"warm ink atmosphere","background":{"mode":"image","file":self.background.name}}
        for beat in data["beats"]:
            beat["motion"]={"from_scale":1,"to_scale":1}
            beat["color_mode"]="original"
        path=self.save(data,"background plan.json")
        work=self.root/"background render work"
        first=renderer.render(path,self.root/"background first.mp4",work,None,1,180,True)
        raw=subprocess.run(["ffmpeg","-v","error","-ss","1","-i",first["output"],"-frames:v","1",
                            "-pix_fmt","rgb24","-f","rawvideo","-"],capture_output=True,check=True).stdout
        pixel=raw[(180*640+80)*3:(180*640+80)*3+3]
        self.assertGreater(pixel[0],pixel[1]+20)
        self.assertGreater(pixel[1],pixel[2]+10)
        foreground=raw[(180*640+320)*3:(180*640+320)*3+3]
        self.assertTrue(all(channel>220 for channel in foreground))
        self.assertLess(max(foreground)-min(foreground),5)
        report=json.loads(Path(first["report"]).read_text(encoding="utf-8"))
        self.assertEqual(report["identity"]["plan"]["background"]["sha256"],renderer.file_hash(self.background))
        second=renderer.render(path,self.root/"background resume.mp4",work,None,1,180,True)
        self.assertEqual(second["reused_segments"],2)
        try:
            png(self.background,640,360,tint=(50,90,150))
            third=renderer.render(path,self.root/"background changed.mp4",work,None,1,180,True)
            self.assertEqual(third["reused_segments"],0)
            self.assertEqual(third["rendered_segments"],2)
            self.assertNotEqual(first["validation"]["sha256"],third["validation"]["sha256"])
        finally:
            png(self.background,640,360,tint=(150,90,50))

    def test_background_change_during_render_is_rejected(self):
        data=copy.deepcopy(self.plan)
        data["visual_identity"]={"background":{"mode":"image","file":self.background.name}}
        original_run=renderer.run
        changed=False
        def change_after_segment(command,*args,**kwargs):
            nonlocal changed
            result=original_run(command,*args,**kwargs)
            if not changed and command[-1].endswith("segment-00001.mp4"):
                png(self.background,640,360,tint=(50,90,150))
                changed=True
            return result
        output=self.root/"changed mid render.mp4"
        try:
            with mock.patch.object(renderer,"run",side_effect=change_after_segment):
                with self.assertRaisesRegex(renderer.RenderError,"Source changed during render"):
                    renderer.render(self.save(data,"changing background.json"),output,
                                    self.root/"changing background work",None,1,180,False)
            self.assertTrue(changed)
            self.assertFalse(output.exists())
        finally:
            png(self.background,640,360,tint=(150,90,50))

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
        # Verify visible explicitly cyan panel plus muted background and actual
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
        self.assertLess(max(early[:3]),60)
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
        changed_easing=copy.deepcopy(self.plan)
        changed_easing["beats"][0]["motion"]["easing"]="linear"
        easing_path=self.save(changed_easing,"pilot.json")
        fourth=renderer.render(easing_path,self.root/"piloto movimento linear.mp4",work,None,1,180,True)
        self.assertEqual(fourth["rendered_segments"],1)
        self.assertEqual(fourth["reused_segments"],1)
        self.assertNotEqual(fourth["validation"]["sha256"],first["validation"]["sha256"])


if __name__=="__main__":
    unittest.main()
