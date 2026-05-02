"""
v2.0 数据迁移

幂等迁移: 将 v1.0 的 ai_configs 表数据迁移到新的 ocr_configs 和 grading_configs 表。
可重复执行——已存在记录时自动跳过。
"""
from sqlalchemy import select, text
from app.db import async_session, engine, Base
from app.models import User, UserRole, AIConfig, OCRConfig, GradingConfig


async def run_v2_migration():
    """执行 v2.0 数据迁移 - 幂等"""
    # 确保新表存在
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        # 检查 ai_configs 表是否存在
        try:
            result = await db.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='ai_configs'"
            ))
            if not result.scalar():
                print("[MIGRATION] ai_configs 表不存在，跳过迁移")
                return
        except Exception:
            print("[MIGRATION] 无法检查 ai_configs 表，跳过迁移")
            return

        old_configs = (await db.execute(select(AIConfig))).scalars().all()
        if not old_configs:
            print("[MIGRATION] 无旧配置数据，跳过")
            return

        student_count = 0
        teacher_count = 0

        for old in old_configs:
            user = await db.get(User, old.user_id)
            if not user:
                continue

            if user.role == UserRole.student:
                existing = await db.get(OCRConfig, (old.user_id,))
                if not existing:
                    db.add(OCRConfig(
                        user_id=old.user_id,
                        model_name=old.ocr_model_name or "glm-4.1v-thinking-flash",
                        api_key_encrypted=old.api_key_encrypted,
                    ))
                    student_count += 1

            elif user.role == UserRole.teacher:
                existing = await db.get(GradingConfig, (old.user_id,))
                if not existing:
                    db.add(GradingConfig(
                        user_id=old.user_id,
                        provider=old.provider or "zhipu",
                        grading_model_name=old.grading_model_name or "GLM-4-Flash-250414",
                        ability_model_name=None,
                        api_key_encrypted=old.api_key_encrypted,
                    ))
                    teacher_count += 1

        await db.commit()
        print(f"[MIGRATION] v2.0 迁移完成: {student_count} 学生OCR配置, {teacher_count} 教师评分配置")
