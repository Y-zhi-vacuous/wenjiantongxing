"""初始化种子数据：深圳中考真题题库 + 测试账号"""
import asyncio
from sqlalchemy import select

from app.db import async_session
from app.models import User, UserRole, EssayTopic, TopicType, TopicGenre, TopicSource, Class, ClassStudent
from app.auth import hash_password


SEED_TOPICS = [
    # 通用深圳中考写作要求：
    # 1. 字数600-900字（少写或多写均可能扣分）
    # 2. 除诗歌外文体不限，以记叙文为主流
    # 3. 文中不得出现真实人名、校名、地名，不可避免时用XXX代替
    # 4. 不得抄袭、套作
    # 5. 语文考试120分钟，作文建议用时45-50分钟
    # 6. 作文满分45分（含书写分3分）

    {"year": 2024, "title": "看，风景在变", "type": TopicType.proposition, "genre": TopicGenre.narrative,
     "difficulty": 3, "word_requirement": 600, "time_minutes": 45,
     "extra_requirements": "不少于600字，不超过900字；除诗歌外文体不限；文中不得出现真实的校名、人名，一律用XXX代替；不得抄袭、套作",
     "tips": "深圳2024中考真题（满分45分）。'风景'可实可虚——可以是自然景色，也可以是人生百态。'在变'是重点，要写出动态变化的过程和你独特的观察与思考。"},

    {"year": 2023, "title": "把学到的用起来真有意义", "type": TopicType.proposition, "genre": TopicGenre.narrative,
     "difficulty": 3, "word_requirement": 600, "time_minutes": 45,
     "extra_requirements": "不少于600字，不超过900字；除诗歌外文体不限；文中不得出现真实的校名、人名，一律用XXX代替",
     "tips": "深圳2023中考真题。核心三个关键词：'学到'+'用'+'有意义'。重点写你学到了什么、怎么运用、产生了什么意义。选材生活化，以小见大。"},

    {"year": 2022, "title": "是你让我超越了平常的自己", "type": TopicType.proposition, "genre": TopicGenre.narrative,
     "difficulty": 4, "word_requirement": 600, "time_minutes": 45,
     "extra_requirements": "不少于600字，不超过900字；除诗歌外文体不限；不得出现真实的校名、人名",
     "tips": "深圳2022中考真题。'你'可以是人、物、事、一句话。重点写'超越'的过程——从平常的自己到不平常的自己，前后对比要鲜明动人。"},

    {"year": 2021, "title": "这创意，让我激动不已", "type": TopicType.proposition, "genre": TopicGenre.narrative,
     "difficulty": 3, "word_requirement": 600, "time_minutes": 50,
     "extra_requirements": "不少于600字；除诗歌外文体不限；不得抄袭套作；文中不得出现真实校名、人名",
     "tips": "深圳2021中考真题（满分48分，含书写3分）。'创意'可以是你的，也可以是别人的。写清楚创意是什么、为什么让你'激动不已'——情感要真挚饱满。"},

    {"year": 2020, "title": "见证美好", "type": TopicType.proposition, "genre": TopicGenre.narrative,
     "difficulty": 2, "word_requirement": 600, "time_minutes": 45,
     "extra_requirements": "不少于600字，不超过900字；除诗歌外文体不限；不得出现真实的校名、人名",
     "tips": "深圳2020中考真题。你是'见证者'而非参与者。通过具体而微的场景写出美好的人与事，强调真情实感，不说大话空话。"},

    {"year": 2019, "title": "因为有我", "type": TopicType.proposition, "genre": TopicGenre.narrative,
     "difficulty": 3, "word_requirement": 600, "time_minutes": 45,
     "extra_requirements": "不少于600字，不超过900字；除诗歌外文体不限；文中不得出现真实的校名、人名",
     "tips": "深圳2019中考真题（满分40分+书写3分）。写'我'对他人/集体的积极影响。要有具体事件支撑，突出'因为'的因果逻辑和你带来的改变。"},

    {"year": 2018, "title": "我与深圳______细节", "type": TopicType.half_proposition, "genre": TopicGenre.narrative,
     "difficulty": 4, "word_requirement": 600, "time_minutes": 50,
     "extra_requirements": "将题目补充完整后作文；不少于600字，不超过900字；除诗歌外文体不限",
     "tips": "深圳2018中考真题。8年中唯一半命题作文。横线处填什么很关键（如'的温暖''的速度''的成长'等）。需写出深圳特色与个人体验的深度融合。"},

    {"year": 2017, "title": "我的动力源", "type": TopicType.proposition, "genre": TopicGenre.narrative,
     "difficulty": 3, "word_requirement": 600, "time_minutes": 45,
     "extra_requirements": "不少于600字，不超过900字；除诗歌外文体不限；不得出现真实的校名、人名",
     "tips": "深圳2017中考真题。写清楚'动力源'是什么（人/物/信念/梦想），通过1-2个具体事例说明它如何持续推动你前进，真情实感最重要。"},

    # 高频模拟题
    {"year": None, "title": "____的眼神", "type": TopicType.half_proposition, "genre": TopicGenre.narrative,
     "difficulty": 3, "word_requirement": 600, "time_minutes": 45,
     "extra_requirements": "将题目补充完整后作文；不少于600字，不超过900字；除诗歌外文体不限",
     "tips": "半命题高频题型。选择印象最深的'眼神'（鼓励/失望/期待/慈爱），通过具体情境让读者感受眼神背后的情感力量。"},

    {"year": None, "title": "阅读下面材料，按要求作文。'每个人心中都有一盏灯，照亮自己，也温暖他人。'请以'心中的那盏灯'为题写一篇文章。",
     "type": TopicType.material, "genre": TopicGenre.narrative,
     "difficulty": 4, "word_requirement": 600, "time_minutes": 50,
     "extra_requirements": "不得脱离材料含义作文；不少于600字，不超过900字；除诗歌外文体不限",
     "tips": "材料作文。'灯'是比喻——可以是理想、亲情、师恩、某种信念。要虚实结合，有具体故事支撑，不能空洞说理。"},
]


async def seed():
    async with async_session() as db:
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("数据库已有数据，跳过种子初始化。如需重置请删除 essay_app.db")
            return

        teacher = User(
            username="teacher1", password_hash=hash_password("test123"),
            role=UserRole.teacher, display_name="李老师",
            real_name="李明远", school="深圳中学实验学校",
            teacher_cert="SZ20210001",
        )
        db.add(teacher)
        await db.flush()

        cls = Class(name="九年级(3)班", teacher_id=teacher.id)
        db.add(cls)
        await db.flush()

        student = User(
            username="student1", password_hash=hash_password("test123"),
            default_password="test123",
            role=UserRole.student, display_name="张小明",
            grade="九年级", school="深圳中学实验学校",
        )
        db.add(student)
        await db.flush()
        db.add(ClassStudent(class_id=cls.id, student_id=student.id))

        for t in SEED_TOPICS:
            title = t["title"]
            if t.get("year"):
                title = f"【{t['year']}年真题】{title}"
            topic = EssayTopic(
                title=title, type=t["type"], genre=t["genre"],
                difficulty=t["difficulty"], tips=t.get("tips"),
                word_requirement=t.get("word_requirement", 600),
                time_minutes=t.get("time_minutes", 45),
                extra_requirements=t.get("extra_requirements"),
                source=TopicSource.system,
            )
            db.add(topic)

        await db.commit()
        print("文鉴同行 — 种子数据初始化完成！")
        print(f"  教师账号: teacher1 / test123 (实名: 李明远)")
        print(f"  学生账号: student1 / test123 (班级: 九年级(3)班)")
        print(f"  深圳中考真题: 8 道 | 高频模拟题: 2 道 | 共 {len(SEED_TOPICS)} 道")


if __name__ == "__main__":
    asyncio.run(seed())
