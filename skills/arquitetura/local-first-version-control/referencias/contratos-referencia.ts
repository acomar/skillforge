export type SyncState =
  | "updated" | "local_changes" | "checking" | "remote_newer"
  | "syncing" | "needs_resolution" | "offline"
  | "permission_lost" | "sync_error" | "integrity_error";

export interface Commit {
  id: string;
  parents: string[];
  snapshotId: string;
  timestamp: string;
  author?: string;
  message?: string;
  schemaVersion: number;
  integrityHash: string;
}

export interface RepositoryManifest {
  formatVersion: number;
  repositoryId: string;
  schemaVersion: number;
}

export type ConflictType =
  | "value_changed_both"
  | "delete_vs_update"
  | "order_conflict"
  | "structural_conflict"
  | "id_collision";

export interface Conflict<T = unknown> {
  conflictId: string;
  path: string;
  entityId?: string;
  type: ConflictType;
  baseValue: T;
  localValue: T;
  remoteValue: T;
  allowedResolutions: Array<"local" | "remote" | "combine" | "edit">;
}

export interface MergeResult<T> {
  value?: T;
  conflicts: Conflict[];
  autoMerged: boolean;
}

export interface RepositoryAdapter {
  connect(): Promise<void>;
  getPermissionState(): Promise<"granted" | "prompt" | "denied" | "unavailable">;
  requestKnownRepositoryPermission(): Promise<boolean>;
  selectRepository?(): Promise<void>;
  readManifest(): Promise<RepositoryManifest>;
  readRef(name: string): Promise<string | null>;
  readObject<T>(id: string): Promise<T>;
  writeImmutableObject<T>(id: string, value: T): Promise<void>;
  compareAndSetRef(name: string, expected: string | null, next: string): Promise<boolean>;
  reconnect(): Promise<void>;
}

export interface LocalStore<T> {
  loadWorkingCopy(): Promise<T>;
  saveWorkingCopy(value: T): Promise<void>;
  getBaseCommit(): Promise<string | null>;
  setBaseCommit(id: string): Promise<void>;
  getLocalHead(): Promise<string | null>;
  setLocalHead(id: string): Promise<void>;
  saveConflictSession(conflicts: Conflict[]): Promise<void>;
}

export interface SemanticMerger<T> {
  diff(base: T, next: T): unknown;
  merge(base: T, local: T, remote: T): Promise<MergeResult<T>>;
}

export interface SyncEngine<T> {
  saveLocalVersion(message?: string): Promise<void>;
  checkRemote(): Promise<SyncState>;
  sync(): Promise<SyncState>;
  resolve(conflictId: string, resolution: unknown): Promise<void>;
  finalizeResolution(): Promise<SyncState>;
}
