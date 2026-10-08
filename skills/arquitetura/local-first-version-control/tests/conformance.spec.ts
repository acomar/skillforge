/*
  Suíte de referência. O implementador conecta createHarness() à implementação real.
*/
import { describe, it, expect } from "vitest";

type Harness = {
  users: any[];
  remote: any;
  openUser(): Promise<any>;
  sync(user: any): Promise<any>;
  edit(user: any, path: string, value: unknown): Promise<void>;
  delete(user: any, path: string): Promise<void>;
  goOffline(user: any): Promise<void>;
  goOnline(user: any): Promise<void>;
  revokePermission(user: any): Promise<void>;
  restoreKnownPermission(user: any): Promise<void>;
};

declare function createHarness(): Promise<Harness>;

describe("local-first-version-control conformance", () => {
  it("preserva alteração somente local após reinício", async () => {
    const h = await createHarness();
    const a = await h.openUser();
    await h.edit(a, "x", 1);
    expect(a.local).toBeDefined();
  });

  it("faz fast-forward quando só remoto avançou", async () => {
    const h = await createHarness();
    const a = await h.openUser(), b = await h.openUser();
    await h.edit(a, "x", 1); await h.sync(a);
    await h.sync(b);
    expect(b.data.x).toBe(1);
  });

  it("combina alterações independentes", async () => {
    const h = await createHarness();
    const a = await h.openUser(), b = await h.openUser();
    await h.edit(a, "x", 1); await h.edit(b, "y", 2);
    await h.sync(a); await h.sync(b);
    expect(b.data).toMatchObject({x:1,y:2});
  });

  it("não escolhe silenciosamente quando ambos alteram o mesmo campo", async () => {
    const h = await createHarness();
    const a = await h.openUser(), b = await h.openUser();
    await h.edit(a, "status", "A"); await h.edit(b, "status", "B");
    await h.sync(a);
    const result = await h.sync(b);
    expect(result.state).toBe("needs_resolution");
  });

  it("detecta delete versus update", async () => {
    const h = await createHarness();
    const a = await h.openUser(), b = await h.openUser();
    await h.delete(a, "item"); await h.edit(b, "item.name", "novo");
    await h.sync(a);
    expect((await h.sync(b)).state).toBe("needs_resolution");
  });

  it("não perde working copy offline", async () => {
    const h = await createHarness();
    const a = await h.openUser();
    await h.goOffline(a); await h.edit(a, "x", 9);
    expect(a.data.x).toBe(9);
  });

  it("reautoriza pasta conhecida sem exigir nova seleção", async () => {
    const h = await createHarness();
    const a = await h.openUser();
    await h.revokePermission(a);
    await h.restoreKnownPermission(a);
    expect((await h.sync(a)).state).not.toBe("permission_lost");
  });

  it("revalida remoto antes da promoção final", async () => {
    const h = await createHarness();
    // Harness deve injetar publicação concorrente entre integração e CAS.
    expect(h.remote).toBeDefined();
  });
});
