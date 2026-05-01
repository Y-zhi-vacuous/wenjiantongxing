import { Routes, Route, Navigate } from 'react-router-dom'
import TeacherNav from '../../components/TeacherNav'
import TeacherDashboard from './Dashboard'
import ClassList from './ClassList'
import ClassDetail from './ClassDetail'
import Topics from './Topics'
import EssayView from './EssayView'
import TeacherSettings from './Settings'

export default function TeacherLayout() {
  return (
    <div className="min-h-screen bg-apple-bg">
      <TeacherNav />
      <main className="max-w-5xl mx-auto px-4 py-8">
        <Routes>
          <Route path="dashboard" element={<TeacherDashboard />} />
          <Route path="classes" element={<ClassList />} />
          <Route path="classes/:id" element={<ClassDetail />} />
          <Route path="topics" element={<Topics />} />
          <Route path="essay/:id" element={<EssayView />} />
          <Route path="settings" element={<TeacherSettings />} />
          <Route path="*" element={<Navigate to="dashboard" replace />} />
        </Routes>
      </main>
    </div>
  )
}
