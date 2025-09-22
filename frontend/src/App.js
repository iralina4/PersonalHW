import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import StudentProfilePage from './pages/StudentProfilePage';
import AssignmentGenerationPage from './pages/AssignmentGenerationPage';
import AssignmentResultPage from './pages/AssignmentResultPage';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/student/:id?" element={<StudentProfilePage />} />
          <Route path="/generate" element={<AssignmentGenerationPage />} />
          <Route path="/assignment/:id" element={<AssignmentResultPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;



