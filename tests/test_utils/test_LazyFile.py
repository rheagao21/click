import os
import threading

import pytest

import click


def test_iter_lazyfile(tmpdir):
    expected = list(map(str, range(10)))
    p = tmpdir.mkdir("testdir").join("testfile")
    p.write("\n".join(expected))
    with p.open() as f:
        with click.utils._LazyFile(f.name) as lf:
            for e_line, a_line in zip(expected, lf, strict=False):
                assert e_line == a_line.strip()


def test_lazy_read_validates_ordinary_path(tmp_path):
    with pytest.raises(FileNotFoundError):
        click.open_file(tmp_path / "missing", lazy=True)


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFO support is required.")
def test_lazy_read_fifo_opens_on_first_read(tmp_path):
    fifo = tmp_path / "fifo"
    os.mkfifo(fifo)
    writer_started = threading.Event()
    writer_opened = threading.Event()

    def write() -> None:
        writer_started.set()

        with fifo.open("wb") as f:
            writer_opened.set()
            f.write(b"data")

    writer = threading.Thread(target=write, daemon=True)
    writer.start()
    assert writer_started.wait(1)

    with click.open_file(fifo, "rb", lazy=True) as f:
        assert not writer_opened.wait(0.1)
        result = []
        reader = threading.Thread(target=lambda: result.append(f.read()), daemon=True)
        reader.start()
        reader.join(1)
        assert not reader.is_alive()
        assert result == [b"data"]

    writer.join(1)
    assert not writer.is_alive()
