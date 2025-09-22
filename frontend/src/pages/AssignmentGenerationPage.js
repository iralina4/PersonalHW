import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { studentsAPI, assignmentsAPI } from '../services/api';

const AssignmentGenerationPage = () => {
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState('');
  const [topicsText, setTopicsText] = useState('');
  const [options, setOptions] = useState({
    count_total: '',
    include_part2: true,
    max_time_min: '',
    make_two_pdfs: true
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadStudents();
  }, []);

  const loadStudents = async () => {
    try {
      const response = await studentsAPI.list();
      setStudents(response.data);
    } catch (error) {
      console.error('Error loading students:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedStudent) {
      alert('Выберите ученика');
      return;
    }

    if (!topicsText.trim()) {
      alert('Введите темы для генерации');
      return;
    }

    try {
      setLoading(true);
      
      const assignmentData = {
        student_id: parseInt(selectedStudent),
        topics_text: topicsText,
        options: {
          count_total: options.count_total ? parseInt(options.count_total) : null,
          include_part2: options.include_part2,
          max_time_min: options.max_time_min ? parseInt(options.max_time_min) : null,
          make_two_pdfs: options.make_two_pdfs
        }
      };

      const response = await assignmentsAPI.generate(assignmentData);
      navigate(`/assignment/${response.data.assignment_id}`);
      
    } catch (error) {
      console.error('Error generating assignment:', error);
      alert('Ошибка при генерации задания');
    } finally {
      setLoading(false);
    }
  };

  const topicSuggestions = [
    'Алгебра — 3, Геометрия — 2, Тригонометрия — 1',
    'Параметры — 2, Планиметрия — 3, Логарифмы — 2',
    'Производные — 2, Интегралы — 1, Неравенства — 2, Часть 2 — 1',
    'Теория вероятностей — 1, Стереометрия — 2, Текстовые задачи — 3'
  ];

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        Генерация домашнего задания
      </h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Выбор ученика</h2>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Ученик *
            </label>
            <select
              required
              value={selectedStudent}
              onChange={(e) => setSelectedStudent(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Выберите ученика</option>
              {students.map(student => (
                <option key={student.id} value={student.id}>
                  {student.name} 
                  {student.profile?.grade && ` (${student.profile.grade} класс)`}
                  {student.profile?.target_score && ` - цель: ${student.profile.target_score} баллов`}
                </option>
              ))}
            </select>
            
            {students.length === 0 && (
              <p className="text-sm text-gray-500 mt-2">
                Нет созданных учеников. 
                <button
                  type="button"
                  onClick={() => navigate('/student')}
                  className="text-primary-500 hover:text-primary-600 ml-1"
                >
                  Создать профиль ученика
                </button>
              </p>
            )}
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Темы и количество задач</h2>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Описание тем *
            </label>
            <textarea
              required
              value={topicsText}
              onChange={(e) => setTopicsText(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              rows="4"
              placeholder="Введите темы и количество задач в свободной форме..."
            />
            
            <div className="mt-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Примеры:</p>
              <div className="space-y-2">
                {topicSuggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => setTopicsText(suggestion)}
                    className="block w-full text-left px-3 py-2 text-sm bg-gray-50 hover:bg-gray-100 rounded border"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Дополнительные опции</h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Общее количество задач
              </label>
              <input
                type="number"
                min="1"
                max="20"
                value={options.count_total}
                onChange={(e) => setOptions(prev => ({ ...prev, count_total: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Оставьте пустым для автоматического подсчета"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Максимальное время (минуты)
              </label>
              <input
                type="number"
                min="10"
                max="300"
                value={options.max_time_min}
                onChange={(e) => setOptions(prev => ({ ...prev, max_time_min: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Ограничение по времени"
              />
            </div>
          </div>

          <div className="mt-6 space-y-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="include_part2"
                checked={options.include_part2}
                onChange={(e) => setOptions(prev => ({ ...prev, include_part2: e.target.checked }))}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="include_part2" className="ml-2 block text-sm text-gray-900">
                Включать задачи части 2 (повышенной сложности)
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="make_two_pdfs"
                checked={options.make_two_pdfs}
                onChange={(e) => setOptions(prev => ({ ...prev, make_two_pdfs: e.target.checked }))}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="make_two_pdfs" className="ml-2 block text-sm text-gray-900">
                Создать два PDF (для ученика и для учителя)
              </label>
            </div>
          </div>
        </div>

        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Отмена
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:opacity-50"
          >
            {loading ? 'Генерация...' : 'Сгенерировать задание'}
          </button>
        </div>
      </form>

      {loading && (
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-500 mr-3"></div>
            <div>
              <p className="font-medium text-blue-900">Генерация задания...</p>
              <p className="text-sm text-blue-700">
                Система анализирует профиль ученика и подбирает персонализированные задачи. 
                Это может занять 1-2 минуты.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AssignmentGenerationPage;



