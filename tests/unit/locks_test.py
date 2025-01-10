# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import asyncio
import typing  # noqa: F401
import unittest
from datetime import timedelta

import pytest
from tornado import gen, locks
from tornado.gen import TimeoutError
from tornado.testing import AsyncTestCase, gen_test


class ConditionTest(AsyncTestCase):
    def setUp(self):
        super().setUp()
        self.history = []  # type: typing.List[typing.Union[int, str]]

    def record_done(self, future, key):
        """Record the resolution of a Future returned by Condition.wait."""

        def callback(_):
            if not future.result():
                # wait() resolved to False, meaning it timed out.
                self.history.append("timeout")
            else:
                self.history.append(key)

        future.add_done_callback(callback)

    def loop_briefly(self):
        """Run all queued callbacks on the IOLoop.

        In these tests, this method is used after calling notify() to
        preserve the pre-5.0 behavior in which callbacks ran
        synchronously.
        """
        self.io_loop.add_callback(self.stop)
        self.wait()

    def test_repr(self):
        c = locks.Condition()
        assert "Condition" in repr(c)
        assert "waiters" not in repr(c)
        c.wait()
        assert "waiters" in repr(c)

    @gen_test
    def test_notify(self):
        c = locks.Condition()
        self.io_loop.call_later(0.01, c.notify)
        yield c.wait()

    def test_notify_1(self):
        c = locks.Condition()
        self.record_done(c.wait(), "wait1")
        self.record_done(c.wait(), "wait2")
        c.notify(1)
        self.loop_briefly()
        self.history.append("notify1")
        c.notify(1)
        self.loop_briefly()
        self.history.append("notify2")
        assert ["wait1", "notify1", "wait2", "notify2"] == self.history

    def test_notify_n(self):
        c = locks.Condition()
        for i in range(6):
            self.record_done(c.wait(), i)

        c.notify(3)
        self.loop_briefly()

        # Callbacks execute in the order they were registered.
        assert list(range(3)) == self.history
        c.notify(1)
        self.loop_briefly()
        assert list(range(4)) == self.history
        c.notify(2)
        self.loop_briefly()
        assert list(range(6)) == self.history

    def test_notify_all(self):
        c = locks.Condition()
        for i in range(4):
            self.record_done(c.wait(), i)

        c.notify_all()
        self.loop_briefly()
        self.history.append("notify_all")

        # Callbacks execute in the order they were registered.
        assert [*list(range(4)), "notify_all"] == self.history  # type: ignore

    @gen_test
    def test_wait_timeout(self):
        c = locks.Condition()
        wait = c.wait(timedelta(seconds=0.01))
        self.io_loop.call_later(0.02, c.notify)  # Too late.
        yield gen.sleep(0.03)
        assert not (yield wait)

    @gen_test
    def test_wait_timeout_preempted(self):
        c = locks.Condition()

        # This fires before the wait times out.
        self.io_loop.call_later(0.01, c.notify)
        wait = c.wait(timedelta(seconds=0.02))
        yield gen.sleep(0.03)
        yield wait  # No TimeoutError.

    @gen_test
    def test_notify_n_with_timeout(self):
        # Register callbacks 0, 1, 2, and 3. Callback 1 has a timeout.
        # Wait for that timeout to expire, then do notify(2) and make
        # sure everyone runs. Verifies that a timed-out callback does
        # not count against the 'n' argument to notify().
        c = locks.Condition()
        self.record_done(c.wait(), 0)
        self.record_done(c.wait(timedelta(seconds=0.01)), 1)
        self.record_done(c.wait(), 2)
        self.record_done(c.wait(), 3)

        # Wait for callback 1 to time out.
        yield gen.sleep(0.02)
        assert ["timeout"] == self.history

        c.notify(2)
        yield gen.sleep(0.01)
        assert ["timeout", 0, 2] == self.history
        assert ["timeout", 0, 2] == self.history
        c.notify()
        yield
        assert ["timeout", 0, 2, 3] == self.history

    @gen_test
    def test_notify_all_with_timeout(self):
        c = locks.Condition()
        self.record_done(c.wait(), 0)
        self.record_done(c.wait(timedelta(seconds=0.01)), 1)
        self.record_done(c.wait(), 2)

        # Wait for callback 1 to time out.
        yield gen.sleep(0.02)
        assert ["timeout"] == self.history

        c.notify_all()
        yield
        assert ["timeout", 0, 2] == self.history

    @gen_test
    def test_nested_notify(self):
        # Ensure no notifications lost, even if notify() is reentered by a
        # waiter calling notify().
        c = locks.Condition()

        # Three waiters.
        futures = [asyncio.ensure_future(c.wait()) for _ in range(3)]

        # First and second futures resolved. Second future reenters notify(),
        # resolving third future.
        futures[1].add_done_callback(lambda _: c.notify())
        c.notify(2)
        yield
        assert all(f.done() for f in futures)

    @gen_test
    def test_garbage_collection(self):
        # Test that timed-out waiters are occasionally cleaned from the queue.
        c = locks.Condition()
        for _ in range(101):
            c.wait(timedelta(seconds=0.01))

        future = asyncio.ensure_future(c.wait())
        assert len(c._waiters) == 102

        # Let first 101 waiters time out, triggering a collection.
        yield gen.sleep(0.02)
        assert len(c._waiters) == 1

        # Final waiter is still active.
        assert not future.done()
        c.notify()
        assert future.done()


class EventTest(AsyncTestCase):
    def test_repr(self):
        event = locks.Event()
        assert "clear" in str(event)
        assert "set" not in str(event)
        event.set()
        assert "clear" not in str(event)
        assert "set" in str(event)

    def test_event(self):
        e = locks.Event()
        future_0 = asyncio.ensure_future(e.wait())
        e.set()
        future_1 = asyncio.ensure_future(e.wait())
        e.clear()
        future_2 = asyncio.ensure_future(e.wait())

        assert future_0.done()
        assert future_1.done()
        assert not future_2.done()

    @gen_test
    def test_event_timeout(self):
        e = locks.Event()
        with pytest.raises(TimeoutError):
            yield e.wait(timedelta(seconds=0.01))

        # After a timed-out waiter, normal operation works.
        self.io_loop.add_timeout(timedelta(seconds=0.01), e.set)
        yield e.wait(timedelta(seconds=1))

    def test_event_set_multiple(self):
        e = locks.Event()
        e.set()
        e.set()
        assert e.is_set()

    def test_event_wait_clear(self):
        e = locks.Event()
        f0 = asyncio.ensure_future(e.wait())
        e.clear()
        f1 = asyncio.ensure_future(e.wait())
        e.set()
        assert f0.done()
        assert f1.done()


class SemaphoreTest(AsyncTestCase):
    def test_negative_value(self):
        self.assertRaises(ValueError, locks.Semaphore, value=-1)

    def test_repr(self):
        sem = locks.Semaphore()
        assert "Semaphore" in repr(sem)
        assert "unlocked,value:1" in repr(sem)
        sem.acquire()
        assert "locked" in repr(sem)
        assert "waiters" not in repr(sem)
        sem.acquire()
        assert "waiters" in repr(sem)

    def test_acquire(self):
        sem = locks.Semaphore()
        f0 = asyncio.ensure_future(sem.acquire())
        assert f0.done()

        # Wait for release().
        f1 = asyncio.ensure_future(sem.acquire())
        assert not f1.done()
        f2 = asyncio.ensure_future(sem.acquire())
        sem.release()
        assert f1.done()
        assert not f2.done()
        sem.release()
        assert f2.done()

        sem.release()
        # Now acquire() is instant.
        assert asyncio.ensure_future(sem.acquire()).done()
        assert len(sem._waiters) == 0

    @gen_test
    def test_acquire_timeout(self):
        sem = locks.Semaphore(2)
        yield sem.acquire()
        yield sem.acquire()
        acquire = sem.acquire(timedelta(seconds=0.01))
        self.io_loop.call_later(0.02, sem.release)  # Too late.
        yield gen.sleep(0.3)
        with pytest.raises(gen.TimeoutError):
            yield acquire

        sem.acquire()
        f = asyncio.ensure_future(sem.acquire())
        assert not f.done()
        sem.release()
        assert f.done()

    @gen_test
    def test_acquire_timeout_preempted(self):
        sem = locks.Semaphore(1)
        yield sem.acquire()

        # This fires before the wait times out.
        self.io_loop.call_later(0.01, sem.release)
        acquire = sem.acquire(timedelta(seconds=0.02))
        yield gen.sleep(0.03)
        yield acquire  # No TimeoutError.

    def test_release_unacquired(self):
        # Unbounded releases are allowed, and increment the semaphore's value.
        sem = locks.Semaphore()
        sem.release()
        sem.release()

        # Now the counter is 3. We can acquire three times before blocking.
        assert asyncio.ensure_future(sem.acquire()).done()
        assert asyncio.ensure_future(sem.acquire()).done()
        assert asyncio.ensure_future(sem.acquire()).done()
        assert not asyncio.ensure_future(sem.acquire()).done()

    @gen_test
    def test_garbage_collection(self):
        # Test that timed-out waiters are occasionally cleaned from the queue.
        sem = locks.Semaphore(value=0)
        futures = [asyncio.ensure_future(sem.acquire(timedelta(seconds=0.01))) for _ in range(101)]

        future = asyncio.ensure_future(sem.acquire())
        assert len(sem._waiters) == 102

        # Let first 101 waiters time out, triggering a collection.
        yield gen.sleep(0.02)
        assert len(sem._waiters) == 1

        # Final waiter is still active.
        assert not future.done()
        sem.release()
        assert future.done()

        # Prevent "Future exception was never retrieved" messages.
        for future in futures:
            self.assertRaises(TimeoutError, future.result)


class SemaphoreContextManagerTest(AsyncTestCase):
    @gen_test
    def test_context_manager(self):
        sem = locks.Semaphore()
        with (yield sem.acquire()) as yielded:
            assert yielded is None

        # Semaphore was released and can be acquired again.
        assert asyncio.ensure_future(sem.acquire()).done()

    @gen_test
    def test_context_manager_async_await(self):
        # Repeat the above test using 'async with'.
        sem = locks.Semaphore()

        async def f():
            async with sem as yielded:
                assert yielded is None

        yield f()

        # Semaphore was released and can be acquired again.
        assert asyncio.ensure_future(sem.acquire()).done()

    @gen_test
    def test_context_manager_exception(self):
        sem = locks.Semaphore()
        with pytest.raises(ZeroDivisionError), (yield sem.acquire()):
            1 / 0

        # Semaphore was released and can be acquired again.
        assert asyncio.ensure_future(sem.acquire()).done()

    @gen_test
    def test_context_manager_timeout(self):
        sem = locks.Semaphore()
        with (yield sem.acquire(timedelta(seconds=0.01))):
            pass

        # Semaphore was released and can be acquired again.
        assert asyncio.ensure_future(sem.acquire()).done()

    @gen_test
    def test_context_manager_timeout_error(self):
        sem = locks.Semaphore(value=0)
        with pytest.raises(gen.TimeoutError):
            with (yield sem.acquire(timedelta(seconds=0.01))):
                pass

        # Counter is still 0.
        assert not asyncio.ensure_future(sem.acquire()).done()

    @gen_test
    def test_context_manager_contended(self):
        sem = locks.Semaphore()
        history = []

        @gen.coroutine
        def f(index):
            with (yield sem.acquire()):
                history.append("acquired %d" % index)
                yield gen.sleep(0.01)
                history.append("release %d" % index)

        yield [f(i) for i in range(2)]

        expected_history = []
        for i in range(2):
            expected_history.extend(["acquired %d" % i, "release %d" % i])

        assert expected_history == history

    @gen_test
    def test_yield_sem(self):
        # Ensure we catch a "with (yield sem)", which should be
        # "with (yield sem.acquire())".
        with pytest.raises(gen.BadYieldError), (yield locks.Semaphore()):
            pass

    def test_context_manager_misuse(self):
        # Ensure we catch a "with sem", which should be
        # "with (yield sem.acquire())".
        with pytest.raises(RuntimeError), locks.Semaphore():
            pass


class BoundedSemaphoreTest(AsyncTestCase):
    def test_release_unacquired(self):
        sem = locks.BoundedSemaphore()
        self.assertRaises(ValueError, sem.release)
        # Value is 0.
        sem.acquire()
        # Block on acquire().
        future = asyncio.ensure_future(sem.acquire())
        assert not future.done()
        sem.release()
        assert future.done()
        # Value is 1.
        sem.release()
        self.assertRaises(ValueError, sem.release)


class LockTests(AsyncTestCase):
    def test_repr(self):
        lock = locks.Lock()
        # No errors.
        repr(lock)
        lock.acquire()
        repr(lock)

    def test_acquire_release(self):
        lock = locks.Lock()
        assert asyncio.ensure_future(lock.acquire()).done()
        future = asyncio.ensure_future(lock.acquire())
        assert not future.done()
        lock.release()
        assert future.done()

    @gen_test
    def test_acquire_fifo(self):
        lock = locks.Lock()
        assert asyncio.ensure_future(lock.acquire()).done()
        N = 5
        history = []

        @gen.coroutine
        def f(idx):
            with (yield lock.acquire()):
                history.append(idx)

        futures = [f(i) for i in range(N)]
        assert not any(future.done() for future in futures)
        lock.release()
        yield futures
        assert list(range(N)) == history

    @gen_test
    def test_acquire_fifo_async_with(self):
        # Repeat the above test using `async with lock:`
        # instead of `with (yield lock.acquire()):`.
        lock = locks.Lock()
        assert asyncio.ensure_future(lock.acquire()).done()
        N = 5
        history = []

        async def f(idx):
            async with lock:
                history.append(idx)

        futures = [f(i) for i in range(N)]
        lock.release()
        yield futures
        assert list(range(N)) == history

    @gen_test
    def test_acquire_timeout(self):
        lock = locks.Lock()
        lock.acquire()
        with pytest.raises(gen.TimeoutError):
            yield lock.acquire(timeout=timedelta(seconds=0.01))

        # Still locked.
        assert not asyncio.ensure_future(lock.acquire()).done()

    def test_multi_release(self):
        lock = locks.Lock()
        self.assertRaises(RuntimeError, lock.release)
        lock.acquire()
        lock.release()
        self.assertRaises(RuntimeError, lock.release)

    @gen_test
    def test_yield_lock(self):
        # Ensure we catch a "with (yield lock)", which should be
        # "with (yield lock.acquire())".
        with pytest.raises(gen.BadYieldError), (yield locks.Lock()):
            pass

    def test_context_manager_misuse(self):
        # Ensure we catch a "with lock", which should be
        # "with (yield lock.acquire())".
        with pytest.raises(RuntimeError), locks.Lock():
            pass


if __name__ == "__main__":
    unittest.main()
