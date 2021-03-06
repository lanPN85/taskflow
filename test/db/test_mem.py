from contextlib import asynccontextmanager
from typing import AsyncIterator
from asynctest import TestCase

from taskflow.model.task import Task, TaskPriority, TaskResourceUsage
from taskflow.db.mem import InMemoryDb


class InMemoryDbTestCase(TestCase):
    @asynccontextmanager
    async def with_db(self) -> AsyncIterator[InMemoryDb]:
        db = InMemoryDb()
        await db.init()

        yield db

        await db.shutdown()

    async def test_flow_1(self):
        async with self.with_db() as db:
            t1 = Task(
                id="1",
                cmd="",
                created_at=0,
                created_by="",
                priority=TaskPriority.MEDIUM,
                usage=TaskResourceUsage(),
            )

            await db.insert_task(t1)

            t1.cmd = "2"
            await db.update_task(t1)

            await db.delete_task(t1)
            pending = await db.get_pending_tasks()
            self.assertEqual(len(pending), 0)

    async def test_flow_2(self):
        async with self.with_db() as db:
            t1 = Task(
                id="1",
                cmd="",
                created_at=0,
                created_by="",
                priority=TaskPriority.MEDIUM,
                usage=TaskResourceUsage(),
            )

            t2 = Task(
                id="2",
                cmd="",
                created_at=1,
                created_by="a",
                priority=TaskPriority.HIGH,
                usage=TaskResourceUsage(),
            )

            await db.insert_task(t1)
            await db.insert_task(t2)

            pending = await db.get_pending_tasks()
            self.assertEqual(len(pending), 2)

            t2.is_running = True
            await db.update_task(t2)

            pending = await db.get_pending_tasks()
            self.assertEqual(len(pending), 1)

            running = await db.get_running_tasks()
            self.assertEqual(len(running), 1)

            l1 = await db.search_tasks()
            self.assertEqual(l1.total, 2)

            l2 = await db.search_tasks(created_by="a")
            self.assertEqual(l2.total, 1)

            l3 = await db.search_tasks(is_running=True)
            self.assertEqual(l3.total, 1)

            l4 = await db.search_tasks(size=1)
            self.assertEqual(l4.total, 2)
            self.assertEqual(len(l4.tasks), 1)
