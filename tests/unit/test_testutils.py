#!/usr/bin/env python3

# Copyright (c) 2009, Giampaolo Rodola'. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Tests for testing utils (psutil.tests namespace)."""

import collections
import contextlib
import errno
import os
import socket
import stat
import subprocess
import unittest

import psutil
import psutil.tests
import pytest
from psutil import FREEBSD, NETBSD, POSIX
from psutil._common import open_binary, open_text, supports_ipv6
from psutil.tests import (
    CI_TESTING,
    COVERAGE,
    HAS_CONNECTIONS_UNIX,
    PYTHON_EXE,
    PYTHON_EXE_ENV,
    PsutilTestCase,
    TestMemoryLeak,
    bind_socket,
    bind_unix_socket,
    call_until,
    chdir,
    create_sockets,
    get_free_port,
    is_namedtuple,
    mock,
    process_namespace,
    reap_children,
    retry,
    retry_on_failure,
    safe_mkdir,
    safe_rmpath,
    serialrun,
    system_namespace,
    tcp_socketpair,
    terminate,
    unix_socketpair,
    wait_for_file,
    wait_for_pid,
)

# ===================================================================
# --- Unit tests for test utilities.
# ===================================================================


class TestRetryDecorator(PsutilTestCase):
    @mock.patch("time.sleep")
    def test_retry_success(self, sleep):
        # Fail 3 times out of 5; make sure the decorated fun returns.

        @retry(retries=5, interval=1, logfun=None)
        def foo():
            while queue:
                queue.pop()
                1 / 0  # noqa
            return 1

        queue = list(range(3))
        assert foo() == 1
        assert sleep.call_count == 3

    @mock.patch("time.sleep")
    def test_retry_failure(self, sleep):
        # Fail 6 times out of 5; th function is supposed to raise exc.
        @retry(retries=5, interval=1, logfun=None)
        def foo():
            while queue:
                queue.pop()
                1 / 0  # noqa
            return 1

        queue = list(range(6))
        self.assertRaises(ZeroDivisionError, foo)
        assert sleep.call_count == 5

    @mock.patch("time.sleep")
    def test_exception_arg(self, sleep):
        @retry(exception=ValueError, interval=1)
        def foo():
            raise TypeError

        self.assertRaises(TypeError, foo)
        assert sleep.call_count == 0

    @mock.patch("time.sleep")
    def test_no_interval_arg(self, sleep):
        # if interval is not specified sleep is not supposed to be called

        @retry(retries=5, interval=None, logfun=None)
        def foo():
            1 / 0  # noqa

        self.assertRaises(ZeroDivisionError, foo)
        assert sleep.call_count == 0

    @mock.patch("time.sleep")
    def test_retries_arg(self, sleep):
        @retry(retries=5, interval=1, logfun=None)
        def foo():
            1 / 0  # noqa

        self.assertRaises(ZeroDivisionError, foo)
        assert sleep.call_count == 5

    @mock.patch("time.sleep")
    def test_retries_and_timeout_args(self, sleep):
        self.assertRaises(ValueError, retry, retries=5, timeout=1)


class TestSyncTestUtils(PsutilTestCase):
    def test_wait_for_pid(self):
        wait_for_pid(os.getpid())
        nopid = max(psutil.pids()) + 99999
        with mock.patch("psutil.tests.retry.__iter__", return_value=iter([0])):
            self.assertRaises(psutil.NoSuchProcess, wait_for_pid, nopid)

    def test_wait_for_file(self):
        testfn = self.get_testfn()
        with open(testfn, "w") as f:
            f.write("foo")
        wait_for_file(testfn)
        assert not os.path.exists(testfn)

    def test_wait_for_file_empty(self):
        testfn = self.get_testfn()
        with open(testfn, "w"):
            pass
        wait_for_file(testfn, empty=True)
        assert not os.path.exists(testfn)

    def test_wait_for_file_no_file(self):
        testfn = self.get_testfn()
        with mock.patch("psutil.tests.retry.__iter__", return_value=iter([0])):
            self.assertRaises(IOError, wait_for_file, testfn)

    def test_wait_for_file_no_delete(self):
        testfn = self.get_testfn()
        with open(testfn, "w") as f:
            f.write("foo")
        wait_for_file(testfn, delete=False)
        assert os.path.exists(testfn)

    def test_call_until(self):
        ret = call_until(lambda: 1, "ret == 1")
        assert ret == 1


class TestFSTestUtils(PsutilTestCase):
    def test_open_text(self):
        with open_text(__file__) as f:
            assert f.mode == "r"

    def test_open_binary(self):
        with open_binary(__file__) as f:
            assert f.mode == "rb"

    def test_safe_mkdir(self):
        testfn = self.get_testfn()
        safe_mkdir(testfn)
        assert os.path.isdir(testfn)
        safe_mkdir(testfn)
        assert os.path.isdir(testfn)

    def test_safe_rmpath(self):
        # test file is removed
        testfn = self.get_testfn()
        open(testfn, "w").close()
        safe_rmpath(testfn)
        assert not os.path.exists(testfn)
        # test no exception if path does not exist
        safe_rmpath(testfn)
        # test dir is removed
        os.mkdir(testfn)
        safe_rmpath(testfn)
        assert not os.path.exists(testfn)
        # test other exceptions are raised
        with mock.patch("psutil.tests.os.stat", side_effect=OSError(errno.EINVAL, "")) as m:
            with pytest.raises(OSError):
                safe_rmpath(testfn)
            assert m.called

    def test_chdir(self):
        testfn = self.get_testfn()
        base = os.getcwd()
        os.mkdir(testfn)
        with chdir(testfn):
            assert os.getcwd() == os.path.join(base, testfn)
        assert os.getcwd() == base


class TestProcessUtils(PsutilTestCase):
    def test_reap_children(self):
        subp = self.spawn_testproc()
        p = psutil.Process(subp.pid)
        assert p.is_running()
        reap_children()
        assert not p.is_running()
        assert not psutil.tests._pids_started
        assert not psutil.tests._subprocesses_started

    def test_spawn_children_pair(self):
        child, grandchild = self.spawn_children_pair()
        assert child.pid != grandchild.pid
        assert child.is_running()
        assert grandchild.is_running()
        children = psutil.Process().children()
        assert children == [child]
        children = psutil.Process().children(recursive=True)
        assert len(children) == 2
        assert child in children
        assert grandchild in children
        assert child.ppid() == os.getpid()
        assert grandchild.ppid() == child.pid

        terminate(child)
        assert not child.is_running()
        assert grandchild.is_running()

        terminate(grandchild)
        assert not grandchild.is_running()

    @unittest.skipIf(not POSIX, "POSIX only")
    def test_spawn_zombie(self):
        parent, zombie = self.spawn_zombie()
        assert zombie.status() == psutil.STATUS_ZOMBIE

    def test_terminate(self):
        # by subprocess.Popen
        p = self.spawn_testproc()
        terminate(p)
        self.assertPidGone(p.pid)
        terminate(p)
        # by psutil.Process
        p = psutil.Process(self.spawn_testproc().pid)
        terminate(p)
        self.assertPidGone(p.pid)
        terminate(p)
        # by psutil.Popen
        cmd = [PYTHON_EXE, "-c", "import time; time.sleep(60);"]
        p = psutil.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=PYTHON_EXE_ENV)
        terminate(p)
        self.assertPidGone(p.pid)
        terminate(p)
        # by PID
        pid = self.spawn_testproc().pid
        terminate(pid)
        self.assertPidGone(p.pid)
        terminate(pid)
        # zombie
        if POSIX:
            parent, zombie = self.spawn_zombie()
            terminate(parent)
            terminate(zombie)
            self.assertPidGone(parent.pid)
            self.assertPidGone(zombie.pid)


class TestNetUtils(PsutilTestCase):
    def bind_socket(self):
        port = get_free_port()
        with contextlib.closing(bind_socket(addr=("", port))) as s:
            assert s.getsockname()[1] == port

    @unittest.skipIf(not POSIX, "POSIX only")
    def test_bind_unix_socket(self):
        name = self.get_testfn()
        sock = bind_unix_socket(name)
        with contextlib.closing(sock):
            assert sock.family == socket.AF_UNIX
            assert sock.type == socket.SOCK_STREAM
            assert sock.getsockname() == name
            assert os.path.exists(name)
            assert stat.S_ISSOCK(os.stat(name).st_mode)
        # UDP
        name = self.get_testfn()
        sock = bind_unix_socket(name, type=socket.SOCK_DGRAM)
        with contextlib.closing(sock):
            assert sock.type == socket.SOCK_DGRAM

    def tcp_tcp_socketpair(self):
        addr = ("127.0.0.1", get_free_port())
        server, client = tcp_socketpair(socket.AF_INET, addr=addr)
        with contextlib.closing(server), contextlib.closing(client):
            # Ensure they are connected and the positions are
            # correct.
            assert server.getsockname() == addr
            assert client.getpeername() == addr
            assert client.getsockname() != addr

    @unittest.skipIf(not POSIX, "POSIX only")
    @unittest.skipIf(NETBSD or FREEBSD, "/var/run/log UNIX socket opened by default")
    def test_unix_socketpair(self):
        p = psutil.Process()
        num_fds = p.num_fds()
        assert not p.connections(kind="unix")
        name = self.get_testfn()
        server, client = unix_socketpair(name)
        try:
            assert os.path.exists(name)
            assert stat.S_ISSOCK(os.stat(name).st_mode)
            assert p.num_fds() - num_fds == 2
            assert len(p.connections(kind="unix")) == 2
            assert server.getsockname() == name
            assert client.getpeername() == name
        finally:
            client.close()
            server.close()

    def test_create_sockets(self):
        with create_sockets() as socks:
            fams = collections.defaultdict(int)
            types = collections.defaultdict(int)
            for s in socks:
                fams[s.family] += 1
                # work around http://bugs.python.org/issue30204
                types[s.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE)] += 1
            assert fams[socket.AF_INET] >= 2
            if supports_ipv6():
                assert fams[socket.AF_INET6] >= 2
            if POSIX and HAS_CONNECTIONS_UNIX:
                assert fams[socket.AF_UNIX] >= 2
            assert types[socket.SOCK_STREAM] >= 2
            assert types[socket.SOCK_DGRAM] >= 2


@serialrun
class TestMemLeakClass(TestMemoryLeak):
    @retry_on_failure()
    def test_times(self):
        def fun():
            cnt["cnt"] += 1

        cnt = {"cnt": 0}
        self.execute(fun, times=10, warmup_times=15)
        assert cnt["cnt"] == 26

    def test_param_err(self):
        self.assertRaises(ValueError, self.execute, lambda: 0, times=0)
        self.assertRaises(ValueError, self.execute, lambda: 0, times=-1)
        self.assertRaises(ValueError, self.execute, lambda: 0, warmup_times=-1)
        self.assertRaises(ValueError, self.execute, lambda: 0, tolerance=-1)
        self.assertRaises(ValueError, self.execute, lambda: 0, retries=-1)

    @retry_on_failure()
    @unittest.skipIf(CI_TESTING, "skipped on CI")
    @unittest.skipIf(COVERAGE, "skipped during test coverage")
    def test_leak_mem(self):
        ls = []

        def fun(ls=ls):
            ls.append("x" * 24 * 1024)

        try:
            # will consume around 3M in total
            self.assertRaisesRegex(AssertionError, "extra-mem", self.execute, fun, times=50)
        finally:
            del ls

    def test_unclosed_files(self):
        def fun():
            f = open(__file__)
            self.addCleanup(f.close)
            box.append(f)

        box = []
        kind = "fd" if POSIX else "handle"
        self.assertRaisesRegex(AssertionError, "unclosed " + kind, self.execute, fun)

    def test_tolerance(self):
        def fun():
            ls.append("x" * 24 * 1024)

        ls = []
        times = 100
        self.execute(fun, times=times, warmup_times=0, tolerance=200 * 1024 * 1024)
        assert len(ls) == times + 1

    def test_execute_w_exc(self):
        def fun_1():
            1 / 0  # noqa

        self.execute_w_exc(ZeroDivisionError, fun_1)
        with pytest.raises(ZeroDivisionError):
            self.execute_w_exc(OSError, fun_1)

        def fun_2():
            pass

        with pytest.raises(AssertionError):
            self.execute_w_exc(ZeroDivisionError, fun_2)


class TestTestingUtils(PsutilTestCase):
    def test_process_namespace(self):
        p = psutil.Process()
        ns = process_namespace(p)
        ns.test()
        fun = next(x for x in ns.iter(ns.getters) if x[1] == "ppid")[0]
        assert fun() == p.ppid()

    def test_system_namespace(self):
        ns = system_namespace()
        fun = next(x for x in ns.iter(ns.getters) if x[1] == "net_if_addrs")[0]
        assert fun() == psutil.net_if_addrs()


class TestOtherUtils(PsutilTestCase):
    def test_is_namedtuple(self):
        assert is_namedtuple(collections.namedtuple("foo", "a b c")(1, 2, 3))
        assert not is_namedtuple(())


if __name__ == "__main__":
    from psutil.tests.runner import run_from_name

    run_from_name(__file__)
