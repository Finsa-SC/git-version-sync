import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from packaging.version import Version

import pytest

# Target modul yang dites
from git_version_sync.core.git import (
    commit_config_change,
    create_github_release,
    delete_remote_tag,
    delete_tag,
    fetch_remote_tags,
    get_git_path,
    get_head_commit,
    get_remote_tags,
    get_tag_commit,
    is_branch_behind_remote,
    push_to_remote,
    reset_soft_head,
)


@pytest.fixture
def temp_git_repo():
    """Membuat temporary git repository untuk isolasi testing integration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)

        # Initialize git repo
        subprocess.run(["git", "init"], capture_output=True, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            capture_output=True,
            check=True,
        )

        # Create initial commit
        Path("pyproject.toml").write_text('version = "1.0.0"')
        subprocess.run(
            ["git", "add", "pyproject.toml"],
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "initial commit"],
            capture_output=True,
            check=True,
        )

        yield tmpdir


class TestGetGitPath:
    """Test get_git_path function."""

    def test_get_git_path_success(self, temp_git_repo):
        """Harus mengembalikan path root git repository."""
        result = get_git_path()
        assert result.resolve() == Path(temp_git_repo).resolve()

    def test_get_git_path_not_a_git_repo(self):
        """Harus melempar RuntimeError ketika berada di luar git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            with pytest.raises(RuntimeError, match="Not a Git repository"):
                get_git_path()


class TestCommitConfigChange:
    """Test commit_config_change function."""

    def test_commit_config_change_success(self, temp_git_repo):
        """Harus berhasil membuat commit perubahan versi."""
        Path("pyproject.toml").write_text('version = "1.1.0"')

        with patch("git_version_sync.core.git.get_config_path") as mock_config:
            mock_config.return_value = Path("pyproject.toml")
            commit_config_change(Version("1.1.0"))

        result = subprocess.run(
            ["git", "log", "--oneline"],
            capture_output=True,
            text=True,
            check=True,
        )
        assert "bump version to v1.1.0" in result.stdout

    def test_commit_nothing_to_commit(self, temp_git_repo):
        """Harus menangani kondisi 'nothing to commit' tanpa melempar error."""
        with patch("git_version_sync.core.git.get_config_path") as mock_config:
            mock_config.return_value = Path("pyproject.toml")
            commit_config_change(Version("1.0.0"))


class TestDeleteTag:
    """Test delete_tag function."""

    def test_delete_tag_success(self, temp_git_repo):
        """Harus berhasil menghapus tag lokal."""
        subprocess.run(
            ["git", "tag", "v1.0.0"],
            capture_output=True,
            check=True,
        )

        delete_tag(Version("1.0.0"))

        result = subprocess.run(
            ["git", "tag", "-l"],
            capture_output=True,
            text=True,
            check=True,
        )
        assert "v1.0.0" not in result.stdout

    def test_delete_tag_nonexistent(self, temp_git_repo):
        """Harus melempar RuntimeError saat menghapus tag yang tidak ada."""
        with pytest.raises(RuntimeError):
            delete_tag(Version("99.0.0"))


class TestDeleteRemoteTag:
    """Test delete_remote_tag function."""

    @patch("subprocess.run")
    def test_delete_remote_tag_success(self, mock_run):
        """Harus memanggil command git push origin --delete secara tepat."""
        mock_run.return_value = MagicMock(returncode=0)

        delete_remote_tag(Version("1.0.0"))

        call_args = mock_run.call_args_list[0][0][0]
        assert "git" in call_args
        assert "push" in call_args
        assert "origin" in call_args
        assert "--delete" in call_args
        assert "v1.0.0" in call_args

    @patch("subprocess.run")
    def test_delete_remote_tag_failure(self, mock_run):
        """Harus melempar RuntimeError jika penghapusan tag remote gagal."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git push", stderr="remote ref does not exist"
        )
        with pytest.raises(RuntimeError):
            delete_remote_tag(Version("99.0.0"))


class TestGetTagCommit:
    """Test get_tag_commit function."""

    def test_get_tag_commit_success(self, temp_git_repo):
        """Harus mengembalikan hash commit yang valid untuk suatu tag."""
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        head_commit = result.stdout.strip()

        subprocess.run(
            ["git", "tag", "v1.0.0"],
            capture_output=True,
            check=True,
        )

        tag_commit = get_tag_commit("v1.0.0")
        assert tag_commit == head_commit

    def test_get_tag_commit_nonexistent(self, temp_git_repo):
        """Harus mengembalikan None jika tag tidak ditemukan."""
        result = get_tag_commit("nonexistent-tag")
        assert result is None


class TestGetHeadCommit:
    """Test get_head_commit function."""

    def test_get_head_commit_success(self, temp_git_repo):
        """Harus mengembalikan SHA commit HEAD saat ini."""
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        expected_commit = result.stdout.strip()

        actual_commit = get_head_commit()
        assert actual_commit == expected_commit
        assert len(actual_commit) == 40


class TestResetSoftHead:
    """Test reset_soft_head function."""

    def test_reset_soft_head_success(self, temp_git_repo):
        """Harus melakukan soft reset HEAD~1 dengan benar."""
        Path("test.txt").write_text("test content")
        subprocess.run(
            ["git", "add", "test.txt"],
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "test commit"],
            capture_output=True,
            check=True,
        )

        result_before = subprocess.run(
            ["git", "log", "--oneline"],
            capture_output=True,
            text=True,
            check=True,
        )
        count_before = len(result_before.stdout.strip().split("\n"))

        reset_soft_head()

        result_after = subprocess.run(
            ["git", "log", "--oneline"],
            capture_output=True,
            text=True,
            check=True,
        )
        count_after = len(result_after.stdout.strip().split("\n"))

        assert count_after == count_before - 1


class TestGetRemoteTags:
    """Test get_remote_tags function."""

    @patch("subprocess.run")
    def test_get_remote_tags_success(self, mock_run):
        """Harus mem-parse daftar tag dari remote secara presisi."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="abc123\trefs/tags/v1.0.0\ndef456\trefs/tags/v1.1.0\n",
        )

        tags = get_remote_tags()
        assert "v1.0.0" in tags
        assert "v1.1.0" in tags

    @patch("subprocess.run")
    def test_get_remote_tags_empty(self, mock_run):
        """Harus mengembalikan set kosong jika tidak ada tag di remote."""
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        tags = get_remote_tags()
        assert len(tags) == 0

    @patch("subprocess.run")
    def test_get_remote_tags_filters_deref(self, mock_run):
        """Harus membuang entri dereference tag annotated (^{})."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="abc123\trefs/tags/v1.0.0\ndef456\trefs/tags/v1.0.0^{}\n",
        )

        tags = get_remote_tags()
        assert tags == {"v1.0.0"}


class TestPushToRemote:
    """Test push_to_remote function."""

    @patch("subprocess.run")
    def test_push_single_version_success(self, mock_run):
        """Harus mem-push satu versi tag ke remote."""
        mock_run.return_value = MagicMock(returncode=0)

        push_to_remote(Version("1.0.0"))

        call_args = mock_run.call_args_list[0][0][0]
        assert "git" in call_args
        assert "push" in call_args
        assert "v1.0.0" in call_args

    @patch("subprocess.run")
    def test_push_multiple_versions_success(self, mock_run):
        """Harus mem-push banyak versi tag sekaligus ke remote."""
        mock_run.return_value = MagicMock(returncode=0)

        versions = [Version("1.0.0"), Version("1.1.0")]
        push_to_remote(versions)

        call_args = mock_run.call_args_list[0][0][0]
        assert "v1.0.0" in call_args
        assert "v1.1.0" in call_args

    @patch("subprocess.run")
    def test_push_to_remote_failure(self, mock_run):
        """Harus melempar RuntimeError jika git push gagal."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git push", stderr="Permission denied"
        )

        with pytest.raises(RuntimeError, match="Failed to push to remote"):
            push_to_remote(Version("1.0.0"))


class TestFetchRemoteTags:
    """Test fetch_remote_tags function."""

    @patch("subprocess.run")
    def test_fetch_remote_tags_success(self, mock_run):
        """Harus berhasil mengambil tag dari remote."""
        mock_run.return_value = MagicMock(returncode=0)

        fetch_remote_tags()

        call_args = mock_run.call_args_list[0][0][0]
        assert "git" in call_args
        assert "fetch" in call_args
        assert "--tags" in call_args

    @patch("subprocess.run")
    def test_fetch_remote_tags_failure(self, mock_run):
        """Harus melempar RuntimeError jika fetch gagal."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git fetch", stderr="Network error"
        )

        with pytest.raises(RuntimeError, match="Failed to fetch tags from remote"):
            fetch_remote_tags()


class TestCreateGithubRelease:
    """Test create_github_release function."""

    @patch("shutil.which")
    @patch("git_version_sync.core.git.push_to_remote")
    @patch("subprocess.run")
    def test_create_github_release_success(self, mock_run, mock_push, mock_which):
        """Harus berhasil membuat GitHub Release via gh CLI."""
        mock_which.return_value = "/usr/bin/gh"
        mock_run.return_value = MagicMock(returncode=0)

        create_github_release(Version("1.0.0"))

        call_args = mock_run.call_args_list[0][0][0]
        assert "gh" in call_args
        assert "release" in call_args
        assert "create" in call_args
        assert "v1.0.0" in call_args

    @patch("shutil.which")
    def test_create_github_release_gh_not_installed(self, mock_which):
        """Harus melempar RuntimeError jika gh CLI belum terpasang."""
        mock_which.return_value = None

        with pytest.raises(RuntimeError, match="Github CLI"):
            create_github_release(Version("1.0.0"))

    @patch("shutil.which")
    @patch("git_version_sync.core.git.push_to_remote")
    @patch("subprocess.run")
    def test_create_github_release_with_message(self, mock_run, mock_push, mock_which):
        """Harus menyertakan opsi --notes saat ada pesan release."""
        mock_which.return_value = "/usr/bin/gh"
        mock_run.return_value = MagicMock(returncode=0)

        create_github_release(
            Version("1.0.0"), message="Bug fixes and improvements"
        )

        call_args = mock_run.call_args_list[0][0][0]
        assert "--notes" in call_args

    @patch("shutil.which")
    @patch("git_version_sync.core.git.push_to_remote")
    @patch("subprocess.run")
    def test_create_github_release_as_draft(self, mock_run, mock_push, mock_which):
        """Harus menyertakan flag --draft jika diset True."""
        mock_which.return_value = "/usr/bin/gh"
        mock_run.return_value = MagicMock(returncode=0)

        create_github_release(Version("1.0.0"), draft=True)

        call_args = mock_run.call_args_list[0][0][0]
        assert "--draft" in call_args


class TestIsBranchBehindRemote:
    """Test is_branch_behind_remote function."""

    @patch("subprocess.run")
    def test_branch_is_behind(self, mock_run):
        """Harus mengembalikan True jika lokal tertinggal commit dari remote."""
        mock_run.return_value = MagicMock(returncode=0, stdout="2\n")
        assert is_branch_behind_remote() is True

    @patch("subprocess.run")
    def test_branch_is_not_behind(self, mock_run):
        """Harus mengembalikan False jika lokal sejajar/di depan remote."""
        mock_run.return_value = MagicMock(returncode=0, stdout="0\n")
        assert is_branch_behind_remote() is False

    @patch("subprocess.run")
    def test_branch_behind_check_failure(self, mock_run):
        """Harus melempar RuntimeError jika pemeriksaan rev-list gagal."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git rev-list", stderr="No upstream configured"
        )
        with pytest.raises(RuntimeError, match="Failed to check branch status"):
            is_branch_behind_remote()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])