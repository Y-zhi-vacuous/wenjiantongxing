import { Routes, Route, Navigate } from 'react-router-dom'
import StudentNav from '../../components/StudentNav'
import Dashboard from './Dashboard'
import WriteEssay from './WriteEssay'
import EssayReport from './EssayReport'
import History from './History'
import Ability from './Ability'
import Settings from './Settings'

export default function StudentLayout() {
  return (
    <div className="min-h-screen bg-[#F2F2F7]">
      <StudentNav />
      <main className="max-w-4xl mx-auto px-5 py-8">
        <Routes>
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="write" element={<WriteEssay />} />
          <Route path="essay/:id" element={<EssayReport />} />
          <Route path="history" element={<History />} />
          <Route path="ability" element={<Ability />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="dashboard" replace />} />
        </Routes>
      </main>
    </div>
  )
}
