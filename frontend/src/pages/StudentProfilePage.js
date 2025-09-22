import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { studentsAPI } from '../services/api';

const StudentProfilePage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [student, setStudent] = useState({
    name: '',
    profile: {
      grade: '',
      exam_date: '',
      target_score: '',
      pace: '',
      weak_topics: [],
      strong_topics: [],
      preferred_task_types: [],
      past_errors: []
    }
  });

  const topicOptions = [
    'Алгебра', 'Геометрия', 'Планиметрия', 'Стереометрия', 
    'Тригонометрия', 'Логарифмы', 'Производные', 'Интегралы',
    'Теория вероятностей', 'Параметры', 'Неравенства'
  ];

  const taskTypeOptions = [
    'Краткий ответ', 'Развернутое решение', 'Выбор варианта',
    'Графики и диаграммы', 'Текстовые задачи', 'Геометрические построения'
  ];

  useEffect(() => {
    if (id) {
      loadStudent();
    }
  }, [id]);

  const loadStudent = async () => {
    try {
      setLoading(true);
      const response = await studentsAPI.get(id);
      setStudent(response.data);
    } catch (error) {
      console.error('Error loading student:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      const studentData = {
        ...student,
        profile: {
          ...student.profile,
          grade: student.profile.grade ? parseInt(student.profile.grade) : null,
          target_score: student.profile.target_score ? parseInt(student.profile.target_score) : null
        }
      };

      if (id) {
        await studentsAPI.update(id, studentData);
      } else {
        const response = await studentsAPI.create(studentData);
        navigate(`/student/${response.data.id}`);
      }
      
      alert('Профиль сохранен успешно!');
    } catch (error) {
      console.error('Error saving student:', error);
      alert('Ошибка при сохранении профиля');
    } finally {
      setLoading(false);
    }
  };

  const handleArrayChange = (field, value) => {
    const items = value.split(',').map(item => item.trim()).filter(item => item);
    setStudent(prev => ({
      ...prev,
      profile: {
        ...prev.profile,
        [field]: items
      }
    }));
  };

  if (loading && id) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        {id ? 'Редактирование профиля ученика' : 'Создание профиля ученика'}
      </h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Основная информация</h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Имя ученика *
              </label>
              <input
                type="text"
                required
                value={student.name}
                onChange={(e) => setStudent(prev => ({ ...prev, name: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Введите имя ученика"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Класс
              </label>
              <select
                value={student.profile.grade}
                onChange={(e) => setStudent(prev => ({
                  ...prev,
                  profile: { ...prev.profile, grade: e.target.value }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Выберите класс</option>
                <option value="10">10 класс</option>
                <option value="11">11 класс</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Дата ЕГЭ
              </label>
              <input
                type="date"
                value={student.profile.exam_date}
                onChange={(e) => setStudent(prev => ({
                  ...prev,
                  profile: { ...prev.profile, exam_date: e.target.value }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Целевой балл
              </label>
              <input
                type="number"
                min="0"
                max="100"
                value={student.profile.target_score}
                onChange={(e) => setStudent(prev => ({
                  ...prev,
                  profile: { ...prev.profile, target_score: e.target.value }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="0-100"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Темп обучения
              </label>
              <select
                value={student.profile.pace}
                onChange={(e) => setStudent(prev => ({
                  ...prev,
                  profile: { ...prev.profile, pace: e.target.value }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Выберите темп</option>
                <option value="slow">Медленный</option>
                <option value="normal">Обычный</option>
                <option value="fast">Быстрый</option>
              </select>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Темы и предпочтения</h2>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Слабые темы
              </label>
              <textarea
                value={student.profile.weak_topics?.join(', ') || ''}
                onChange={(e) => handleArrayChange('weak_topics', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                rows="3"
                placeholder="Введите темы через запятую (например: Логарифмы, Тригонометрия, Параметры)"
              />
              <p className="text-sm text-gray-500 mt-1">
                Доступные темы: {topicOptions.join(', ')}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Сильные темы
              </label>
              <textarea
                value={student.profile.strong_topics?.join(', ') || ''}
                onChange={(e) => handleArrayChange('strong_topics', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                rows="3"
                placeholder="Введите темы через запятую"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Предпочитаемые типы заданий
              </label>
              <textarea
                value={student.profile.preferred_task_types?.join(', ') || ''}
                onChange={(e) => handleArrayChange('preferred_task_types', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                rows="3"
                placeholder="Введите типы заданий через запятую"
              />
              <p className="text-sm text-gray-500 mt-1">
                Доступные типы: {taskTypeOptions.join(', ')}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Прошлые ошибки
              </label>
              <textarea
                value={student.profile.past_errors?.join(', ') || ''}
                onChange={(e) => handleArrayChange('past_errors', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                rows="3"
                placeholder="Опишите типичные ошибки ученика через запятую"
              />
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
            {loading ? 'Сохранение...' : 'Сохранить профиль'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default StudentProfilePage;



