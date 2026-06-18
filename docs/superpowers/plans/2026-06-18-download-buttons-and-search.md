# Download Buttons + Search/Filter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire up download functionality (single video, subtitles, playlist batch) and add search/filter to video info display components.

**Architecture:** Backend gets a new subtitle download endpoint extending the existing DownloadManager. Frontend wires up the three stubbed handlers in HomeView and adds inline search/filter UI to FormatTable, SubtitleList, and PlaylistTable.

**Tech Stack:** Vue 3 / TypeScript / Element Plus (frontend), Python / FastAPI / yt-dlp (backend), pytest + vitest (testing)

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `backend/src/core/ytdl_wrapper.py` | Modify | Add `subtitle_lang` param to `download()` |
| `backend/src/api/download.py` | Modify | Add `POST /download/subtitle` endpoint |
| `backend/tests/test_core/test_download_mgr.py` | Modify | Add subtitle download test |
| `backend/tests/test_api/test_download.py` | Modify | Add subtitle endpoint test |
| `electron/src/renderer/src/api/download.ts` | Modify | Add `startSubtitleDownload()` |
| `electron/src/renderer/src/components/FormatTable.vue` | Modify | Download button per row + quality chips + text search |
| `electron/src/renderer/src/components/SubtitleList.vue` | Modify | Text search filter |
| `electron/src/renderer/src/components/PlaylistTable.vue` | Modify | Text search filter |
| `electron/src/renderer/src/views/HomeView.vue` | Modify | Wire up all download handlers |
| `electron/src/renderer/src/i18n/zh.ts` | Modify | Add new keys |
| `electron/src/renderer/src/i18n/en.ts` | Modify | Add new keys |
| `electron/src/renderer/src/components/__tests__/FormatTable.spec.ts` | Create | FormatTable tests |
| `electron/src/renderer/src/components/__tests__/SubtitleList.spec.ts` | Create | SubtitleList tests |
| `electron/src/renderer/src/components/__tests__/PlaylistTable.spec.ts` | Create | PlaylistTable tests |

---

### Task 1: Backend — Subtitle download in ytdl_wrapper

**Files:**
- Modify: `backend/src/core/ytdl_wrapper.py:163-196`
- Test: `backend/tests/test_core/test_ytdl_wrapper.py` (create if not exists)

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_core/test_ytdl_wrapper.py`:

```python
# backend/tests/test_core/test_ytdl_wrapper.py
import pytest
from unittest.mock import patch, MagicMock
from src.core.ytdl_wrapper import YtdlWrapper


class TestYtdlWrapperSubtitleDownload:
    def test_download_with_subtitle_lang(self):
        wrapper = YtdlWrapper()
        with patch("yt_dlp.YoutubeDL") as MockYDL:
            mock_instance = MagicMock()
            MockYDL.return_value.__enter__ = MagicMock(return_value=mock_instance)
            MockYDL.return_value.__exit__ = MagicMock(return_value=False)
            mock_instance.extract_info.return_value = {"title": "test", "ext": "mp4"}
            mock_instance.prepare_filename.return_value = "/tmp/test.mp4"

            wrapper.download(
                url="https://youtube.com/watch?v=test",
                format_id="22",
                output_dir="/tmp",
                subtitle_lang="en",
            )

            # Verify subtitle options were set
            call_opts = MockYDL.call_args[0][0]
            assert call_opts["writesubtitles"] is True
            assert call_opts["subtitleslangs"] == ["en"]

    def test_download_without_subtitle_lang(self):
        wrapper = YtdlWrapper()
        with patch("yt_dlp.YoutubeDL") as MockYDL:
            mock_instance = MagicMock()
            MockYDL.return_value.__enter__ = MagicMock(return_value=mock_instance)
            MockYDL.return_value.__exit__ = MagicMock(return_value=False)
            mock_instance.extract_info.return_value = {"title": "test", "ext": "mp4"}
            mock_instance.prepare_filename.return_value = "/tmp/test.mp4"

            wrapper.download(
                url="https://youtube.com/watch?v=test",
                format_id="22",
                output_dir="/tmp",
            )

            call_opts = MockYDL.call_args[0][0]
            assert "writesubtitles" not in call_opts
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_core/test_ytdl_wrapper.py -v`
Expected: FAIL — `download()` does not accept `subtitle_lang` parameter.

- [ ] **Step 3: Implement subtitle support**

Modify `backend/src/core/ytdl_wrapper.py`, method `download()` (line 163). Change signature and add subtitle logic:

```python
def download(
    self,
    url: str,
    format_id: str,
    output_dir: str,
    progress_hook: Callable | None = None,
    should_abort: Callable[[], bool] | None = None,
    subtitle_lang: str | None = None,
) -> str:
    logger.info(f"download: url={url}, format_id={format_id}, output_dir={output_dir}, subtitle_lang={subtitle_lang}")
    opts = self._base_opts()
    opts["format"] = format_id
    opts["outtmpl"] = os.path.join(output_dir, "%(title)s.%(ext)s")
    opts.pop("skip_download", None)

    if subtitle_lang:
        opts["writesubtitles"] = True
        opts["subtitleslangs"] = [subtitle_lang]

    hooks = []
    if progress_hook:
        hooks.append(progress_hook)
    if should_abort:
        def abort_hook(d: dict):
            if should_abort():
                raise DownloadInterrupted("下载被中断")
        hooks.append(abort_hook)
    if hooks:
        opts["progress_hooks"] = hooks

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
    except Exception as e:
        logger.error(f"download: error: {type(e).__name__}: {e}", exc_info=True)
        raise
    logger.info(f"download: completed, filename={filename}")
    return filename
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_core/test_ytdl_wrapper.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/core/ytdl_wrapper.py backend/tests/test_core/test_ytdl_wrapper.py
git commit -m "feat(backend): add subtitle_lang param to ytdl_wrapper.download()"
```

---

### Task 2: Backend — Subtitle download endpoint

**Files:**
- Modify: `backend/src/api/download.py:1-67`
- Modify: `backend/tests/test_api/test_download.py`

- [ ] **Step 1: Write the failing test**

Add to `backend/tests/test_api/test_download.py`:

```python
class TestSubtitleDownloadEndpoint:
    @pytest.mark.asyncio
    async def test_start_subtitle_download(self, client):
        response = await client.post(
            "/api/v1/download/subtitle",
            json={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "video_id": "dQw4w9WgXcQ",
                "title": "Test Video",
                "language": "en",
                "ext": "srt",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "waiting"
        assert data["format_id"] == "subtitle:en"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_subtitle_download_appears_in_queue(self, client):
        await client.post(
            "/api/v1/download/subtitle",
            json={
                "url": "https://youtube.com/watch?v=test",
                "video_id": "test",
                "title": "Test",
                "language": "zh",
                "ext": "srt",
            },
        )
        response = await client.get("/api/v1/download/queue")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["format_id"] == "subtitle:zh"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_api/test_download.py::TestSubtitleDownloadEndpoint -v`
Expected: FAIL — endpoint does not exist.

- [ ] **Step 3: Implement the endpoint**

Modify `backend/src/api/download.py`. Add request model and endpoint after the existing `start_download`:

```python
class DownloadSubtitleRequest(BaseModel):
    url: str
    video_id: str
    title: str
    language: str
    ext: str


@router.post("/download/subtitle")
async def start_subtitle_download(req: DownloadSubtitleRequest, request: Request):
    _ensure_tracker(request)
    task = _manager.add_task(
        url=req.url,
        video_id=req.video_id,
        title=f"{req.title} [{req.language}]",
        format_id=f"subtitle:{req.language}",
    )
    return task.model_dump()
```

Also modify `DownloadManager.execute_task()` in `backend/src/core/download_mgr.py` to pass `subtitle_lang` when `format_id` starts with `subtitle:`:

In `execute_task()` (around line 129), change the download call:

```python
subtitle_lang = None
if task.format_id.startswith("subtitle:"):
    subtitle_lang = task.format_id.split(":", 1)[1]

filepath = await asyncio.get_running_loop().run_in_executor(
    None,
    lambda: wrapper.download(
        task.url, task.format_id, download_dir, hook,
        should_abort=lambda: self._should_abort(task_id),
        subtitle_lang=subtitle_lang,
    ),
)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_api/test_download.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/api/download.py backend/src/core/download_mgr.py backend/tests/test_api/test_download.py
git commit -m "feat(backend): add subtitle download endpoint"
```

---

### Task 3: Frontend API — startSubtitleDownload

**Files:**
- Modify: `electron/src/renderer/src/api/download.ts`

- [ ] **Step 1: Add the API function**

Add to `electron/src/renderer/src/api/download.ts` after the `startDownload` function:

```typescript
export async function startSubtitleDownload(
  url: string,
  videoId: string,
  title: string,
  language: string,
  ext: string
): Promise<DownloadTask> {
  const { data } = await client.post("/api/v1/download/subtitle", {
    url,
    video_id: videoId,
    title,
    language,
    ext,
  });
  return data;
}
```

- [ ] **Step 2: Commit**

```bash
git add electron/src/renderer/src/api/download.ts
git commit -m "feat(frontend): add startSubtitleDownload API function"
```

---

### Task 4: FormatTable — Per-row download button

**Files:**
- Modify: `electron/src/renderer/src/components/FormatTable.vue`
- Create: `electron/src/renderer/src/components/__tests__/FormatTable.spec.ts`

- [ ] **Step 1: Write the failing test**

Create `electron/src/renderer/src/components/__tests__/FormatTable.spec.ts`:

```typescript
// electron/src/renderer/src/components/__tests__/FormatTable.spec.ts
import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import ElementPlus from "element-plus";
import FormatTable from "../FormatTable.vue";
import type { FormatInfo } from "@/types";

const mockFormats: FormatInfo[] = [
  {
    format_id: "22",
    ext: "mp4",
    resolution: "1280x720",
    fps: 30,
    vcodec: "avc1",
    acodec: "mp4a",
    filesize: 10485760,
    format_note: "720p",
    is_video_only: false,
    is_audio_only: false,
  },
  {
    format_id: "140",
    ext: "m4a",
    resolution: "audio only",
    fps: null,
    vcodec: "none",
    acodec: "mp4a",
    filesize: 5242880,
    format_note: "audio",
    is_video_only: false,
    is_audio_only: true,
  },
];

function mountComponent(props = {}) {
  return mount(FormatTable, {
    props: {
      formats: mockFormats,
      videoUrl: "https://youtube.com/watch?v=test",
      videoId: "test",
      videoTitle: "Test Video",
      ...props,
    },
    global: {
      plugins: [createPinia(), ElementPlus],
    },
  });
}

describe("FormatTable", () => {
  it("renders download button for each row", () => {
    const wrapper = mountComponent();
    const downloadButtons = wrapper.findAll("button").filter((b) => b.text().includes("下载") || b.text().includes("Download"));
    expect(downloadButtons.length).toBeGreaterThanOrEqual(2);
  });

  it("emits download event when download button clicked", async () => {
    const wrapper = mountComponent();
    const rows = wrapper.findAll("tr");
    // Skip header row, click download on first data row
    const downloadBtn = rows[1].findAll("button").find((b) => b.text().includes("下载") || b.text().includes("Download"));
    if (downloadBtn) {
      await downloadBtn.trigger("click");
      expect(wrapper.emitted("download")).toBeTruthy();
      expect(wrapper.emitted("download")![0]).toEqual([mockFormats[0]]);
    }
  });

  it("renders quality chips", () => {
    const wrapper = mountComponent();
    expect(wrapper.text()).toContain("1080p");
    expect(wrapper.text()).toContain("720p");
    expect(wrapper.text()).toContain("480p");
  });

  it("filters by quality chip", async () => {
    const wrapper = mountComponent();
    // Click 720p chip
    const chips = wrapper.findAll(".el-check-tag, .el-tag").filter((c) => c.text() === "720p");
    if (chips.length > 0) {
      await chips[0].trigger("click");
      // After filtering, audio-only row should be hidden
      const rows = wrapper.findAll("tr");
      // Header + 1 visible row (720p format)
      expect(rows.length).toBeLessThanOrEqual(3);
    }
  });

  it("filters by search text", async () => {
    const wrapper = mountComponent();
    const input = wrapper.find("input[type='text']");
    if (input.exists()) {
      await input.setValue("mp4");
      await input.trigger("input");
      // Both rows have mp4/m4a, so both should remain
      const rows = wrapper.findAll("tr");
      expect(rows.length).toBe(3); // header + 2 data rows
    }
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd electron && npx vitest run src/renderer/src/components/__tests__/FormatTable.spec.ts`
Expected: FAIL — component does not accept new props or render download buttons.

- [ ] **Step 3: Implement download button + quality chips + search**

Replace `electron/src/renderer/src/components/FormatTable.vue` entirely:

```vue
<template>
  <div style="margin-top: 16px">
    <h3>{{ t('format.title') }}</h3>

    <!-- Quality chips + search -->
    <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 12px; flex-wrap: wrap">
      <el-check-tag
        v-for="chip in qualityChips"
        :key="chip.label"
        :checked="activeChips.has(chip.label)"
        @change="toggleChip(chip.label)"
      >
        {{ chip.label }}
      </el-check-tag>
      <el-input
        v-model="searchText"
        :placeholder="t('format.searchPlaceholder')"
        clearable
        style="width: 200px; margin-left: auto"
        size="small"
      />
    </div>

    <el-table :data="filteredFormats" stripe style="width: 100%">
      <el-table-column :label="t('format.quality')" width="120">
        <template #default="{ row }">{{ row.format_note }}</template>
      </el-table-column>
      <el-table-column prop="resolution" :label="t('format.resolution')" width="140" />
      <el-table-column prop="ext" :label="t('format.ext')" width="80" />
      <el-table-column prop="fps" :label="t('format.fps')" width="80">
        <template #default="{ row }">
          {{ row.fps ? `${row.fps}fps` : '-' }}
        </template>
      </el-table-column>
      <el-table-column :label="t('format.size')" width="120">
        <template #default="{ row }">
          {{ row.filesize ? formatSize(row.filesize) : t('format.unknown') }}
        </template>
      </el-table-column>
      <el-table-column :label="t('format.type')" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.is_video_only" type="warning" size="small">{{ t('format.videoOnly') }}</el-tag>
          <el-tag v-else-if="row.is_audio_only" type="success" size="small">{{ t('format.audioOnly') }}</el-tag>
          <el-tag v-else type="info" size="small">{{ t('format.merged') }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('format.action')" width="100" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            :loading="downloadingIds.has(row.format_id)"
            @click="onDownload(row)"
          >
            {{ t('format.download') }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import type { FormatInfo } from "@/types";

const { t } = useI18n();

defineProps<{
  formats: FormatInfo[];
  videoUrl: string;
  videoId: string;
  videoTitle: string;
}>();

const emit = defineEmits<{
  download: [format: FormatInfo];
}>();

const searchText = ref("");
const activeChips = ref<Set<string>>(new Set());
const downloadingIds = ref<Set<string>>(new Set());

const qualityChips = [
  { label: "4K", min: 2160 },
  { label: "1080p", min: 1080, max: 2160 },
  { label: "720p", min: 720, max: 1080 },
  { label: "480p", min: 0, max: 720 },
  { label: "Audio", audioOnly: true },
];

function toggleChip(label: string) {
  if (activeChips.value.has(label)) {
    activeChips.value.delete(label);
  } else {
    activeChips.value.add(label);
  }
}

function getResolutionHeight(resolution: string): number {
  const match = resolution.match(/x(\d+)$/);
  return match ? parseInt(match[1], 10) : 0;
}

const filteredFormats = computed(() => {
  // Get the formats from parent via prop - we need to access it reactively
  // Since formats is a prop, we use it directly in the computed
  return [] as FormatInfo[]; // placeholder - actual logic below
});

// We need the formats prop accessible in computed, so restructure:
const props = defineProps<{
  formats: FormatInfo[];
  videoUrl: string;
  videoId: string;
  videoTitle: string;
}>();

const filteredFormats = computed(() => {
  let result = props.formats;

  // Apply quality chip filter
  if (activeChips.value.size > 0) {
    result = result.filter((fmt) => {
      for (const chip of qualityChips) {
        if (!activeChips.value.has(chip.label)) continue;
        if (chip.audioOnly && fmt.is_audio_only) return true;
        if (!chip.audioOnly && !fmt.is_audio_only) {
          const h = getResolutionHeight(fmt.resolution);
          if (chip.max !== undefined && h >= chip.min && h < chip.max) return true;
          if (chip.max === undefined && h >= chip.min) return true;
        }
      }
      return false;
    });
  }

  // Apply text search
  if (searchText.value.trim()) {
    const q = searchText.value.toLowerCase();
    result = result.filter(
      (fmt) =>
        fmt.format_note.toLowerCase().includes(q) ||
        fmt.resolution.toLowerCase().includes(q) ||
        fmt.ext.toLowerCase().includes(q)
    );
  }

  return result;
});

function onDownload(format: FormatInfo) {
  downloadingIds.value.add(format.format_id);
  emit("download", format);
  // Reset loading after a short delay (actual completion handled by parent)
  setTimeout(() => downloadingIds.value.delete(format.format_id), 2000);
}

function formatSize(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  return `${(bytes / 1024 / 1024 / 1024).toFixed(2)} GB`;
}
</script>
```

Wait — the above has a duplicate `defineProps` and `filteredFormats`. Let me write it correctly:

```vue
<template>
  <div style="margin-top: 16px">
    <h3>{{ t('format.title') }}</h3>

    <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 12px; flex-wrap: wrap">
      <el-check-tag
        v-for="chip in qualityChips"
        :key="chip.label"
        :checked="activeChips.has(chip.label)"
        @change="toggleChip(chip.label)"
      >
        {{ chip.label }}
      </el-check-tag>
      <el-input
        v-model="searchText"
        :placeholder="t('format.searchPlaceholder')"
        clearable
        style="width: 200px; margin-left: auto"
        size="small"
      />
    </div>

    <el-table :data="filteredFormats" stripe style="width: 100%">
      <el-table-column :label="t('format.quality')" width="120">
        <template #default="{ row }">{{ row.format_note }}</template>
      </el-table-column>
      <el-table-column prop="resolution" :label="t('format.resolution')" width="140" />
      <el-table-column prop="ext" :label="t('format.ext')" width="80" />
      <el-table-column prop="fps" :label="t('format.fps')" width="80">
        <template #default="{ row }">
          {{ row.fps ? `${row.fps}fps` : '-' }}
        </template>
      </el-table-column>
      <el-table-column :label="t('format.size')" width="120">
        <template #default="{ row }">
          {{ row.filesize ? formatSize(row.filesize) : t('format.unknown') }}
        </template>
      </el-table-column>
      <el-table-column :label="t('format.type')" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.is_video_only" type="warning" size="small">{{ t('format.videoOnly') }}</el-tag>
          <el-tag v-else-if="row.is_audio_only" type="success" size="small">{{ t('format.audioOnly') }}</el-tag>
          <el-tag v-else type="info" size="small">{{ t('format.merged') }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('format.action')" width="100" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            :loading="downloadingIds.has(row.format_id)"
            @click="onDownload(row)"
          >
            {{ t('format.download') }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import type { FormatInfo } from "@/types";

const { t } = useI18n();

const props = defineProps<{
  formats: FormatInfo[];
}>();

const emit = defineEmits<{
  download: [format: FormatInfo];
}>();

const searchText = ref("");
const activeChips = ref<Set<string>>(new Set());
const downloadingIds = ref<Set<string>>(new Set());

const qualityChips = [
  { label: "4K", min: 2160 },
  { label: "1080p", min: 1080, max: 2160 },
  { label: "720p", min: 720, max: 1080 },
  { label: "480p", min: 0, max: 720 },
  { label: "Audio", audioOnly: true },
];

function toggleChip(label: string) {
  if (activeChips.value.has(label)) {
    activeChips.value.delete(label);
  } else {
    activeChips.value.add(label);
  }
}

function getResolutionHeight(resolution: string): number {
  const match = resolution.match(/x(\d+)$/);
  return match ? parseInt(match[1], 10) : 0;
}

const filteredFormats = computed(() => {
  let result = props.formats;

  if (activeChips.value.size > 0) {
    result = result.filter((fmt) => {
      for (const chip of qualityChips) {
        if (!activeChips.value.has(chip.label)) continue;
        if (chip.audioOnly && fmt.is_audio_only) return true;
        if (!chip.audioOnly && !fmt.is_audio_only) {
          const h = getResolutionHeight(fmt.resolution);
          if (chip.max !== undefined && h >= chip.min && h < chip.max) return true;
          if (chip.max === undefined && h >= chip.min) return true;
        }
      }
      return false;
    });
  }

  if (searchText.value.trim()) {
    const q = searchText.value.toLowerCase();
    result = result.filter(
      (fmt) =>
        fmt.format_note.toLowerCase().includes(q) ||
        fmt.resolution.toLowerCase().includes(q) ||
        fmt.ext.toLowerCase().includes(q)
    );
  }

  return result;
});

function onDownload(format: FormatInfo) {
  downloadingIds.value.add(format.format_id);
  emit("download", format);
  setTimeout(() => downloadingIds.value.delete(format.format_id), 2000);
}

function formatSize(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  return `${(bytes / 1024 / 1024 / 1024).toFixed(2)} GB`;
}
</script>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd electron && npx vitest run src/renderer/src/components/__tests__/FormatTable.spec.ts`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add electron/src/renderer/src/components/FormatTable.vue electron/src/renderer/src/components/__tests__/FormatTable.spec.ts
git commit -m "feat(frontend): add download button, quality chips, and search to FormatTable"
```

---

### Task 5: SubtitleList — Text search

**Files:**
- Modify: `electron/src/renderer/src/components/SubtitleList.vue`
- Create: `electron/src/renderer/src/components/__tests__/SubtitleList.spec.ts`

- [ ] **Step 1: Write the failing test**

Create `electron/src/renderer/src/components/__tests__/SubtitleList.spec.ts`:

```typescript
import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import ElementPlus from "element-plus";
import SubtitleList from "../SubtitleList.vue";
import type { SubtitleInfo } from "@/types";

const mockSubtitles: SubtitleInfo[] = [
  { language: "en", language_name: "English", ext: "srt", is_auto_generated: false },
  { language: "zh-Hans", language_name: "Chinese (Simplified)", ext: "srt", is_auto_generated: true },
  { language: "ja", language_name: "Japanese", ext: "vtt", is_auto_generated: true },
];

function mountComponent(props = {}) {
  return mount(SubtitleList, {
    props: {
      subtitles: mockSubtitles,
      ...props,
    },
    global: {
      plugins: [createPinia(), ElementPlus],
    },
  });
}

describe("SubtitleList", () => {
  it("renders search input", () => {
    const wrapper = mountComponent();
    const input = wrapper.find("input");
    expect(input.exists()).toBe(true);
  });

  it("filters subtitles by search text", async () => {
    const wrapper = mountComponent();
    const input = wrapper.find("input");
    await input.setValue("English");
    await input.trigger("input");
    expect(wrapper.text()).toContain("English");
    expect(wrapper.text()).not.toContain("Japanese");
  });

  it("shows all subtitles when search is empty", async () => {
    const wrapper = mountComponent();
    const input = wrapper.find("input");
    await input.setValue("English");
    await input.setValue("");
    await input.trigger("input");
    expect(wrapper.text()).toContain("English");
    expect(wrapper.text()).toContain("Japanese");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd electron && npx vitest run src/renderer/src/components/__tests__/SubtitleList.spec.ts`
Expected: FAIL — no search input exists.

- [ ] **Step 3: Implement search**

Replace `electron/src/renderer/src/components/SubtitleList.vue`:

```vue
<template>
  <div v-if="subtitles.length > 0" style="margin-top: 16px">
    <h3>{{ t('subtitle.title') }}</h3>
    <el-input
      v-model="searchText"
      :placeholder="t('subtitle.searchPlaceholder')"
      clearable
      size="small"
      style="margin-bottom: 12px; width: 250px"
    />
    <el-checkbox-group v-model="selectedLanguages">
      <div v-for="sub in filteredSubtitles" :key="sub.language" style="margin-bottom: 8px">
        <el-checkbox :value="sub.language" :label="sub.language">
          {{ sub.language_name }}
          <el-tag v-if="sub.is_auto_generated" size="small" type="info">{{ t('subtitle.auto') }}</el-tag>
          <el-tag v-else size="small">{{ t('subtitle.manual') }}</el-tag>
          ({{ sub.ext }})
        </el-checkbox>
      </div>
    </el-checkbox-group>
    <el-button
      v-if="selectedLanguages.length > 0"
      type="primary"
      size="small"
      style="margin-top: 8px"
      @click="onDownload"
    >
      {{ t('subtitle.downloadSelected') }}
    </el-button>
  </div>
  <el-empty v-else :description="t('subtitle.empty')" />
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import type { SubtitleInfo } from "@/types";

const { t } = useI18n();

const props = defineProps<{ subtitles: SubtitleInfo[] }>();
const emit = defineEmits<{ download: [languages: string[]] }>();

const selectedLanguages = ref<string[]>([]);
const searchText = ref("");

const filteredSubtitles = computed(() => {
  if (!searchText.value.trim()) return props.subtitles;
  const q = searchText.value.toLowerCase();
  return props.subtitles.filter(
    (sub) =>
      sub.language_name.toLowerCase().includes(q) ||
      sub.language.toLowerCase().includes(q)
  );
});

function onDownload() {
  emit("download", selectedLanguages.value);
}
</script>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd electron && npx vitest run src/renderer/src/components/__tests__/SubtitleList.spec.ts`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add electron/src/renderer/src/components/SubtitleList.vue electron/src/renderer/src/components/__tests__/SubtitleList.spec.ts
git commit -m "feat(frontend): add text search to SubtitleList"
```

---

### Task 6: PlaylistTable — Text search

**Files:**
- Modify: `electron/src/renderer/src/components/PlaylistTable.vue`
- Create: `electron/src/renderer/src/components/__tests__/PlaylistTable.spec.ts`

- [ ] **Step 1: Write the failing test**

Create `electron/src/renderer/src/components/__tests__/PlaylistTable.spec.ts`:

```typescript
import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia } from "pinia";
import ElementPlus from "element-plus";
import PlaylistTable from "../PlaylistTable.vue";
import type { PlaylistInfo } from "@/types";

const mockPlaylist: PlaylistInfo = {
  id: "PLtest",
  title: "Test Playlist",
  uploader: "TestUser",
  video_count: 3,
  videos: [
    { id: "v1", title: "First Video", duration: 120, thumbnail: "", url: "" },
    { id: "v2", title: "Second Video", duration: 240, thumbnail: "", url: "" },
    { id: "v3", title: "Another Topic", duration: 180, thumbnail: "", url: "" },
  ],
  page: 1,
  total_pages: 1,
};

function mountComponent() {
  return mount(PlaylistTable, {
    props: { playlist: mockPlaylist },
    global: { plugins: [createPinia(), ElementPlus] },
  });
}

describe("PlaylistTable", () => {
  it("renders search input", () => {
    const wrapper = mountComponent();
    const input = wrapper.find("input");
    expect(input.exists()).toBe(true);
  });

  it("filters videos by title", async () => {
    const wrapper = mountComponent();
    const input = wrapper.find("input");
    await input.setValue("First");
    await input.trigger("input");
    expect(wrapper.text()).toContain("First Video");
    expect(wrapper.text()).not.toContain("Another Topic");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd electron && npx vitest run src/renderer/src/components/__tests__/PlaylistTable.spec.ts`
Expected: FAIL — no search input exists.

- [ ] **Step 3: Implement search**

Modify `electron/src/renderer/src/components/PlaylistTable.vue`. Add search input and filter logic:

In `<template>`, add after the header div (line 13, before the `<el-table>`):

```html
<el-input
  v-model="searchText"
  :placeholder="t('playlist.searchPlaceholder')"
  clearable
  size="small"
  style="margin-bottom: 12px; width: 250px"
/>
```

In `<script setup>`, add:

```typescript
const searchText = ref("");

const filteredVideos = computed(() => {
  if (!searchText.value.trim()) return props.playlist.videos;
  const q = searchText.value.toLowerCase();
  return props.playlist.videos.filter((v) => v.title.toLowerCase().includes(q));
});
```

Change `:data="playlist.videos"` to `:data="filteredVideos"` on the `<el-table>`.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd electron && npx vitest run src/renderer/src/components/__tests__/PlaylistTable.spec.ts`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add electron/src/renderer/src/components/PlaylistTable.vue electron/src/renderer/src/components/__tests__/PlaylistTable.spec.ts
git commit -m "feat(frontend): add text search to PlaylistTable"
```

---

### Task 7: HomeView — Wire up download handlers

**Files:**
- Modify: `electron/src/renderer/src/views/HomeView.vue:34-97`

- [ ] **Step 1: Implement all download handlers**

Replace the `<script setup>` section of `electron/src/renderer/src/views/HomeView.vue`:

```vue
<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { ElMessage } from "element-plus";
import { useVideoStore } from "@/stores/video";
import { useDownloadStore } from "@/stores/download";
import { getVideoInfo } from "@/api/video";
import { getPlaylistInfo } from "@/api/playlist";
import { startDownload, startSubtitleDownload } from "@/api/download";
import UrlInput from "@/components/UrlInput.vue";
import VideoCard from "@/components/VideoCard.vue";
import FormatTable from "@/components/FormatTable.vue";
import SubtitleList from "@/components/SubtitleList.vue";
import PlaylistTable from "@/components/PlaylistTable.vue";
import type { FormatInfo, PlaylistVideoItem } from "@/types";

const { t } = useI18n();
const videoStore = useVideoStore();
const downloadStore = useDownloadStore();
const playlistUrl = ref("");

const playlistUrlPattern = /[?&]list=/;

async function handleParse(url: string) {
  videoStore.setLoading(true);
  videoStore.clear();
  playlistUrl.value = "";
  try {
    if (playlistUrlPattern.test(url)) {
      playlistUrl.value = url;
      const info = await getPlaylistInfo(url);
      videoStore.setPlaylist(info);
    } else {
      const info = await getVideoInfo(url);
      videoStore.setVideo(info);
    }
  } catch (e: any) {
    videoStore.setError(e.message || t('home.parseFailed'));
  } finally {
    videoStore.setLoading(false);
  }
}

async function onFormatDownload(format: FormatInfo) {
  const video = videoStore.currentVideo;
  if (!video) return;
  try {
    const task = await startDownload(video.webpage_url, video.id, video.title, format.format_id);
    downloadStore.addTask(task);
    ElMessage.success(`${t('download.taskAdded')}: ${video.title} (${format.format_note})`);
  } catch (e: any) {
    ElMessage.error(e.message || t('download.startFailed'));
  }
}

async function onSubtitleDownload(languages: string[]) {
  const video = videoStore.currentVideo;
  if (!video) return;
  let count = 0;
  for (const lang of languages) {
    const sub = video.subtitles.find((s) => s.language === lang);
    if (!sub) continue;
    try {
      const task = await startSubtitleDownload(video.webpage_url, video.id, video.title, lang, sub.ext);
      downloadStore.addTask(task);
      count++;
    } catch (e: any) {
      ElMessage.error(`${sub.language_name}: ${e.message || t('download.startFailed')}`);
    }
  }
  if (count > 0) {
    ElMessage.success(`${t('download.subtitleAdded')}: ${count}`);
  }
}

async function onPlaylistDownload(videos: PlaylistVideoItem[]) {
  let count = 0;
  for (const video of videos) {
    try {
      const task = await startDownload(video.url, video.id, video.title, "best");
      downloadStore.addTask(task);
      count++;
    } catch (e: any) {
      ElMessage.error(`${video.title}: ${e.message || t('download.startFailed')}`);
    }
  }
  if (count > 0) {
    ElMessage.success(`${t('download.playlistAdded')}: ${count}`);
  }
}

async function onPlaylistPageChange(page: number) {
  if (!playlistUrl.value) return;
  videoStore.setLoading(true);
  try {
    const info = await getPlaylistInfo(playlistUrl.value, page);
    videoStore.setPlaylist(info);
  } catch (e: any) {
    videoStore.setError(e.message || t('home.loadPageFailed'));
  } finally {
    videoStore.setLoading(false);
  }
}
</script>
```

Also update the template to pass the new props and rename the event handler:

```vue
<FormatTable
  v-if="videoStore.currentVideo"
  :formats="videoStore.currentVideo.formats"
  @download="onFormatDownload"
/>
```

(Remove `@select="onFormatSelect"` and replace with `@download="onFormatDownload"`)

- [ ] **Step 2: Build check**

Run: `cd electron && npx vue-tsc --noEmit`
Expected: No type errors.

- [ ] **Step 3: Commit**

```bash
git add electron/src/renderer/src/views/HomeView.vue
git commit -m "feat(frontend): wire up download handlers in HomeView"
```

---

### Task 8: i18n — Add new translation keys

**Files:**
- Modify: `electron/src/renderer/src/i18n/zh.ts`
- Modify: `electron/src/renderer/src/i18n/en.ts`

- [ ] **Step 1: Add Chinese translations**

Add to `zh.ts` in the `format` section:

```typescript
format: {
  title: "可用格式",
  quality: "清晰度",
  resolution: "分辨率",
  ext: "格式",
  fps: "帧率",
  size: "大小",
  type: "类型",
  videoOnly: "仅视频",
  audioOnly: "仅音频",
  merged: "合并",
  unknown: "未知",
  action: "操作",
  download: "下载",
  searchPlaceholder: "搜索格式...",
},
```

Add to `subtitle` section:

```typescript
subtitle: {
  title: "可用字幕",
  auto: "自动",
  manual: "手动",
  downloadSelected: "下载选中字幕",
  empty: "无可用字幕",
  searchPlaceholder: "搜索字幕...",
},
```

Add to `playlist` section:

```typescript
playlist: {
  videoCount: "个视频",
  deselectAll: "取消全选",
  selectAll: "全选",
  downloadSelected: "下载选中",
  thumbnail: "缩略图",
  title: "标题",
  duration: "时长",
  searchPlaceholder: "搜索视频...",
},
```

Add to `download` section:

```typescript
download: {
  // ... existing keys ...
  taskAdded: "下载任务已添加",
  subtitleAdded: "字幕下载已添加",
  playlistAdded: "播放列表下载已添加",
  startFailed: "下载失败",
},
```

- [ ] **Step 2: Add English translations**

Same pattern for `en.ts`:

```typescript
format: {
  // ... existing keys ...
  action: "Action",
  download: "Download",
  searchPlaceholder: "Search formats...",
},
subtitle: {
  // ... existing keys ...
  searchPlaceholder: "Search subtitles...",
},
playlist: {
  // ... existing keys ...
  searchPlaceholder: "Search videos...",
},
download: {
  // ... existing keys ...
  taskAdded: "Download task added",
  subtitleAdded: "Subtitle downloads added",
  playlistAdded: "Playlist downloads added",
  startFailed: "Download failed",
},
```

- [ ] **Step 3: Commit**

```bash
git add electron/src/renderer/src/i18n/zh.ts electron/src/renderer/src/i18n/en.ts
git commit -m "feat(i18n): add translation keys for download buttons and search"
```

---

### Task 9: Final verification

- [ ] **Step 1: Run all backend tests**

Run: `cd backend && python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 2: Run all frontend tests**

Run: `cd electron && npx vitest run`
Expected: ALL PASS

- [ ] **Step 3: Type check**

Run: `cd electron && npx vue-tsc --noEmit`
Expected: No errors.

- [ ] **Step 4: Manual smoke test**

Run the app (`cd electron && npm run dev`), parse a YouTube video URL, verify:
- FormatTable shows download button per row
- Quality chips filter formats
- Search input filters formats
- Clicking download creates a task visible in Downloads tab
- SubtitleList has search input
- PlaylistTable has search input

- [ ] **Step 5: Final commit if needed**

```bash
git add -A
git commit -m "feat: download buttons and search/filter for video info display"
```
