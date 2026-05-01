export default function TeacherSettings() {
  return (
    <div className="max-w-lg space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-apple-text tracking-tight">设置</h2>
        <p className="text-apple-secondary mt-1">教师账号设置</p>
      </div>
      <div className="bg-white rounded-apple shadow-apple p-6">
        <h3 className="font-semibold text-apple-text mb-3">关于</h3>
        <p className="text-sm text-apple-secondary leading-relaxed">
          作文提升智能助手 v1.0 · 教师端<br />
          支持班级管理、题库管理和学生作文批改查看。
        </p>
      </div>
    </div>
  )
}
