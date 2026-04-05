import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <div className="flex items-center justify-center min-h-screen text-2xl font-bold text-teal-400">
              DentAI — Day 1 Scaffold ✅
            </div>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App
