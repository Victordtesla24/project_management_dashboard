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
import unittest
from datetime import timedelta
from random import random

import pytest
from tornado import gen, queues
from tornado.gen import TimeoutError
from tornado.testing import AsyncTestCase, gen_test


class QueueBasicTest(AsyncTestCase):
    def test_repr_and_str(self):
        q = queues.Queue(maxsize=1)  # type: queues.Queue[None]
        assert hex(id(q)) in repr(q)
        assert hex(id(q)) not in str(q)
        q.get()

        for q_str in repr(q), str(q):
            assert q_str.startswith("<Queue")
            assert "maxsize=1" in q_str
            assert "getters[1]" in q_str
            assert "putters" not in q_str
            assert "tasks" not in q_str

        q.put(None)
        q.put(None)
        # Now the queue is full, this putter blocks.
        q.put(None)

        for q_str in repr(q), str(q):
            assert "getters" not in q_str
            assert "putters[1]" in q_str
            assert "tasks=2" in q_str

    def test_order(self):
        q = queues.Queue()  # type: queues.Queue[int]
        for i in [1, 3, 2]:
            q.put_nowait(i)

        items = [q.get_nowait() for _ in range(3)]
        assert [1, 3, 2] == items

    @gen_test
    def test_maxsize(self):
        self.assertRaises(TypeError, queues.Queue, maxsize=None)
        self.assertRaises(ValueError, queues.Queue, maxsize=-1)

        q = queues.Queue(maxsize=2)  # type: queues.Queue[int]
        assert q.empty()
        assert not q.full()
        assert q.maxsize == 2
        assert q.put(0).done()
        assert q.put(1).done()
        assert not q.empty()
        assert q.full()
        put2 = q.put(2)
        assert not put2.done()
        assert (yield q.get()) == 0  # Make room.
        assert put2.done()
        assert not q.empty()
        assert q.full()


class QueueGetTest(AsyncTestCase):
    @gen_test
    def test_blocking_get(self):
        q = queues.Queue()  # type: queues.Queue[int]
        q.put_nowait(0)
        assert (yield q.get()) == 0

    def test_nonblocking_get(self):
        q = queues.Queue()  # type: queues.Queue[int]
        q.put_nowait(0)
        assert q.get_nowait() == 0

    def test_nonblocking_get_exception(self):
        q = queues.Queue()  # type: queues.Queue[int]
        self.assertRaises(queues.QueueEmpty, q.get_nowait)

    @gen_test
    def test_get_with_putters(self):
        q = queues.Queue(1)  # type: queues.Queue[int]
        q.put_nowait(0)
        put = q.put(1)
        assert (yield q.get()) == 0
        assert (yield put) is None

    @gen_test
    def test_blocking_get_wait(self):
        q = queues.Queue()  # type: queues.Queue[int]
        q.put(0)
        self.io_loop.call_later(0.01, q.put_nowait, 1)
        self.io_loop.call_later(0.02, q.put_nowait, 2)
        assert (yield q.get(timeout=timedelta(seconds=1))) == 0
        assert (yield q.get(timeout=timedelta(seconds=1))) == 1

    @gen_test
    def test_get_timeout(self):
        q = queues.Queue()  # type: queues.Queue[int]
        get_timeout = q.get(timeout=timedelta(seconds=0.01))
        get = q.get()
        with pytest.raises(TimeoutError):
            yield get_timeout

        q.put_nowait(0)
        assert (yield get) == 0

    @gen_test
    def test_get_timeout_preempted(self):
        q = queues.Queue()  # type: queues.Queue[int]
        get = q.get(timeout=timedelta(seconds=0.01))
        q.put(0)
        yield gen.sleep(0.02)
        assert (yield get) == 0

    @gen_test
    def test_get_clears_timed_out_putters(self):
        q = queues.Queue(1)  # type: queues.Queue[int]
        # First putter succeeds, remainder block.
        putters = [q.put(i, timedelta(seconds=0.01)) for i in range(10)]
        put = q.put(10)
        assert len(q._putters) == 10
        yield gen.sleep(0.02)
        assert len(q._putters) == 10
        assert not put.done()  # Final waiter is still active.
        q.put(11)
        assert (yield q.get()) == 0  # get() clears the waiters.
        assert len(q._putters) == 1
        for putter in putters[1:]:
            self.assertRaises(TimeoutError, putter.result)

    @gen_test
    def test_get_clears_timed_out_getters(self):
        q = queues.Queue()  # type: queues.Queue[int]
        getters = [asyncio.ensure_future(q.get(timedelta(seconds=0.01))) for _ in range(10)]
        get = asyncio.ensure_future(q.get())
        assert len(q._getters) == 11
        yield gen.sleep(0.02)
        assert len(q._getters) == 11
        assert not get.done()  # Final waiter is still active.
        q.get()  # get() clears the waiters.
        assert len(q._getters) == 2
        for getter in getters:
            self.assertRaises(TimeoutError, getter.result)

    @gen_test
    def test_async_for(self):
        q = queues.Queue()  # type: queues.Queue[int]
        for i in range(5):
            q.put(i)

        async def f():
            results = []
            async for i in q:
                results.append(i)
                if i == 4:
                    return results
            return None

        results = yield f()
        assert results == list(range(5))


class QueuePutTest(AsyncTestCase):
    @gen_test
    def test_blocking_put(self):
        q = queues.Queue()  # type: queues.Queue[int]
        q.put(0)
        assert q.get_nowait() == 0

    def test_nonblocking_put_exception(self):
        q = queues.Queue(1)  # type: queues.Queue[int]
        q.put(0)
        self.assertRaises(queues.QueueFull, q.put_nowait, 1)

    @gen_test
    def test_put_with_getters(self):
        q = queues.Queue()  # type: queues.Queue[int]
        get0 = q.get()
        get1 = q.get()
        yield q.put(0)
        assert (yield get0) == 0
        yield q.put(1)
        assert (yield get1) == 1

    @gen_test
    def test_nonblocking_put_with_getters(self):
        q = queues.Queue()  # type: queues.Queue[int]
        get0 = q.get()
        get1 = q.get()
        q.put_nowait(0)
        # put_nowait does *not* immediately unblock getters.
        yield gen.moment
        assert (yield get0) == 0
        q.put_nowait(1)
        yield gen.moment
        assert (yield get1) == 1

    @gen_test
    def test_blocking_put_wait(self):
        q = queues.Queue(1)  # type: queues.Queue[int]
        q.put_nowait(0)

        def get_and_discard():
            q.get()

        self.io_loop.call_later(0.01, get_and_discard)
        self.io_loop.call_later(0.02, get_and_discard)
        futures = [q.put(0), q.put(1)]
        assert not any(f.done() for f in futures)
        yield futures

    @gen_test
    def test_put_timeout(self):
        q = queues.Queue(1)  # type: queues.Queue[int]
        q.put_nowait(0)  # Now it's full.
        put_timeout = q.put(1, timeout=timedelta(seconds=0.01))
        put = q.put(2)
        with pytest.raises(TimeoutError):
            yield put_timeout

        assert q.get_nowait() == 0
        # 1 was never put in the queue.
        assert (yield q.get()) == 2

        # Final get() unblocked this putter.
        yield put

    @gen_test
    def test_put_timeout_preempted(self):
        q = queues.Queue(1)  # type: queues.Queue[int]
        q.put_nowait(0)
        put = q.put(1, timeout=timedelta(seconds=0.01))
        q.get()
        yield gen.sleep(0.02)
        yield put  # No TimeoutError.

    @gen_test
    def test_put_clears_timed_out_putters(self):
        q = queues.Queue(1)  # type: queues.Queue[int]
        # First putter succeeds, remainder block.
        putters = [q.put(i, timedelta(seconds=0.01)) for i in range(10)]
        put = q.put(10)
        assert len(q._putters) == 10
        yield gen.sleep(0.02)
        assert len(q._putters) == 10
        assert not put.done()  # Final waiter is still active.
        q.put(11)  # put() clears the waiters.
        assert len(q._putters) == 2
        for putter in putters[1:]:
            self.assertRaises(TimeoutError, putter.result)

    @gen_test
    def test_put_clears_timed_out_getters(self):
        q = queues.Queue()  # type: queues.Queue[int]
        getters = [asyncio.ensure_future(q.get(timedelta(seconds=0.01))) for _ in range(10)]
        get = asyncio.ensure_future(q.get())
        q.get()
        assert len(q._getters) == 12
        yield gen.sleep(0.02)
        assert len(q._getters) == 12
        assert not get.done()  # Final waiters still active.
        q.put(0)  # put() clears the waiters.
        assert len(q._getters) == 1
        assert (yield get) == 0
        for getter in getters:
            self.assertRaises(TimeoutError, getter.result)

    @gen_test
    def test_float_maxsize(self):
        # If a float is passed for maxsize, a reasonable limit should
        # be enforced, instead of being treated as unlimited.
        # It happens to be rounded up.
        # http://bugs.python.org/issue21723
        q = queues.Queue(maxsize=1.3)  # type: ignore
        assert q.empty()
        assert not q.full()
        q.put_nowait(0)
        q.put_nowait(1)
        assert not q.empty()
        assert q.full()
        self.assertRaises(queues.QueueFull, q.put_nowait, 2)
        assert q.get_nowait() == 0
        assert not q.empty()
        assert not q.full()

        yield q.put(2)
        put = q.put(3)
        assert not put.done()
        assert (yield q.get()) == 1
        yield put
        assert q.full()


class QueueJoinTest(AsyncTestCase):
    queue_class = queues.Queue

    def test_task_done_underflow(self):
        q = self.queue_class()  # type: queues.Queue
        self.assertRaises(ValueError, q.task_done)

    @gen_test
    def test_task_done(self):
        q = self.queue_class()  # type: queues.Queue
        for i in range(100):
            q.put_nowait(i)

        self.accumulator = 0

        @gen.coroutine
        def worker():
            while True:
                item = yield q.get()
                self.accumulator += item
                q.task_done()
                yield gen.sleep(random() * 0.01)

        # Two coroutines share work.
        worker()
        worker()
        yield q.join()
        assert sum(range(100)) == self.accumulator

    @gen_test
    def test_task_done_delay(self):
        # Verify it is task_done(), not get(), that unblocks join().
        q = self.queue_class()  # type: queues.Queue
        q.put_nowait(0)
        join = asyncio.ensure_future(q.join())
        assert not join.done()
        yield q.get()
        assert not join.done()
        yield gen.moment
        assert not join.done()
        q.task_done()
        assert join.done()

    @gen_test
    def test_join_empty_queue(self):
        q = self.queue_class()  # type: queues.Queue
        yield q.join()
        yield q.join()

    @gen_test
    def test_join_timeout(self):
        q = self.queue_class()  # type: queues.Queue
        q.put(0)
        with pytest.raises(TimeoutError):
            yield q.join(timeout=timedelta(seconds=0.01))


class PriorityQueueJoinTest(QueueJoinTest):
    queue_class = queues.PriorityQueue

    @gen_test
    def test_order(self):
        q = self.queue_class(maxsize=2)
        q.put_nowait((1, "a"))
        q.put_nowait((0, "b"))
        assert q.full()
        q.put((3, "c"))
        q.put((2, "d"))
        assert q.get_nowait() == (0, "b")
        assert (yield q.get()) == (1, "a")
        assert q.get_nowait() == (2, "d")
        assert (yield q.get()) == (3, "c")
        assert q.empty()


class LifoQueueJoinTest(QueueJoinTest):
    queue_class = queues.LifoQueue

    @gen_test
    def test_order(self):
        q = self.queue_class(maxsize=2)
        q.put_nowait(1)
        q.put_nowait(0)
        assert q.full()
        q.put(3)
        q.put(2)
        assert q.get_nowait() == 3
        assert (yield q.get()) == 2
        assert q.get_nowait() == 0
        assert (yield q.get()) == 1
        assert q.empty()


class ProducerConsumerTest(AsyncTestCase):
    @gen_test
    def test_producer_consumer(self):
        q = queues.Queue(maxsize=3)  # type: queues.Queue[int]
        history = []

        # We don't yield between get() and task_done(), so get() must wait for
        # the next tick. Otherwise we'd immediately call task_done and unblock
        # join() before q.put() resumes, and we'd only process the first four
        # items.
        @gen.coroutine
        def consumer():
            while True:
                history.append((yield q.get()))
                q.task_done()

        @gen.coroutine
        def producer():
            for item in range(10):
                yield q.put(item)

        consumer()
        yield producer()
        yield q.join()
        assert list(range(10)) == history


if __name__ == "__main__":
    unittest.main()
