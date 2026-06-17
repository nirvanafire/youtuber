from src.models.download import DownloadTask, DownloadProgress, DownloadStatus


class TestDownloadStatus:
    def test_all_statuses_exist(self):
        assert DownloadStatus.WAITING == "waiting"
        assert DownloadStatus.DOWNLOADING == "downloading"
        assert DownloadStatus.PAUSED == "paused"
        assert DownloadStatus.COMPLETED == "completed"
        assert DownloadStatus.FAILED == "failed"
        assert DownloadStatus.CANCELLED == "cancelled"


class TestDownloadTask:
    def test_create_task(self):
        task = DownloadTask(
            id="task-001",
            video_id="dQw4w9WgXcQ",
            title="Never Gonna Give You Up",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            format_id="22",
            status=DownloadStatus.WAITING,
        )
        assert task.id == "task-001"
        assert task.status == DownloadStatus.WAITING
        assert task.progress is None

    def test_task_defaults(self):
        task = DownloadTask(
            id="task-002",
            video_id="test",
            title="Test",
            url="https://youtube.com/watch?v=test",
            format_id="best",
            status=DownloadStatus.WAITING,
        )
        assert task.progress is None
        assert task.filepath is None
        assert task.error is None


class TestDownloadProgress:
    def test_create_progress(self):
        progress = DownloadProgress(
            percent=45.2,
            speed=1_500_000,
            downloaded_bytes=45_000_000,
            total_bytes=100_000_000,
            eta=37,
        )
        assert progress.percent == 45.2
        assert progress.speed == 1_500_000
        assert progress.eta == 37

    def test_progress_unknown_total(self):
        progress = DownloadProgress(
            percent=50.0,
            speed=1_000_000,
            downloaded_bytes=50_000_000,
            total_bytes=None,
            eta=None,
        )
        assert progress.total_bytes is None
        assert progress.eta is None
