import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { assignmentsAPI } from '../services/api';

const AssignmentResultPage = () => {
  const { id } = useParams();
  const [assignment, setAssignment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState({ student: false, teacher: false });

  useEffect(() => {
    loadAssignment();
    const interval = setInterval(loadAssignment, 5000);
    return () => clearInterval(interval);
  }, [id]);

  const loadAssignment = async () => {
    try {
      const response = await assignmentsAPI.get(id);
      setAssignment(response.data);
      
      if (response.data.status === 'completed' || response.data.status === 'failed') {
        setLoading(false);
      }
    } catch (error) {
      console.error('Error loading assignment:', error);
      setLoading(false);
    }
  };

  const downloadPDF = async (type) => {
    try {
      setDownloading(prev => ({ ...prev, [type]: true }));
      
      const response = await assignmentsAPI.downloadPDF(id, type);
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `assignment_${id}_${type}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Ошибка при скачивании PDF');
    } finally {
      setDownloading(prev => ({ ...prev, [type]: false }));
    }
  };

  if (!assignment) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">Загрузка...</div>
      </div>
    );
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'processing': return 'text-blue-600 bg-blue-100';
      case 'failed': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed': return 'Завершено';
      case 'processing': return 'Обработка';
      case 'failed': return 'Ошибка';
      case 'pending': return 'В очереди';
      default: return status;
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        Результат генерации задания
      </h1>

      <div className="space-y-6">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Статус задания</h2>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(assignment.status)}`}>
              {getStatusText(assignment.status)}
            </span>
          </div>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">ID задания</p>
              <p className="font-medium">#{assignment.id}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Ученик</p>
              <p className="font-medium">{assignment.student?.name || 'Не указан'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Дата создания</p>
              <p className="font-medium">
                {new Date(assignment.created_at).toLocaleString('ru-RU')}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Количество задач</p>
              <p className="font-medium">{assignment.items?.length || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Темы задания</h2>
          <div className="bg-gray-50 p-4 rounded-md">
            <p className="text-gray-700">{assignment.topics_text}</p>
          </div>
        </div>

        {assignment.status === 'processing' && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mr-3"></div>
              <div>
                <p className="font-medium text-blue-900">Задание обрабатывается...</p>
                <p className="text-sm text-blue-700">
                  Система подбирает персонализированные задачи и генерирует PDF документы. 
                  Страница автоматически обновится при завершении.
                </p>
              </div>
            </div>
          </div>
        )}

        {assignment.status === 'failed' && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center">
              <div className="text-red-500 mr-3">❌</div>
              <div>
                <p className="font-medium text-red-900">Ошибка при генерации задания</p>
                <p className="text-sm text-red-700">
                  Произошла ошибка при обработке запроса. Попробуйте создать новое задание.
                </p>
              </div>
            </div>
          </div>
        )}

        {assignment.status === 'completed' && (
          <>
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Скачать PDF</h2>
              
              <div className="grid md:grid-cols-2 gap-4">
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center mb-3">
                    <div className="text-2xl mr-3">👨‍🎓</div>
                    <div>
                      <h3 className="font-medium">Версия для ученика</h3>
                      <p className="text-sm text-gray-600">Задачи без ответов и решений</p>
                    </div>
                  </div>
                  <button
                    onClick={() => downloadPDF('student')}
                    disabled={downloading.student}
                    className="w-full bg-primary-500 text-white px-4 py-2 rounded hover:bg-primary-600 disabled:opacity-50"
                  >
                    {downloading.student ? 'Скачивание...' : 'Скачать PDF ученика'}
                  </button>
                </div>

                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center mb-3">
                    <div className="text-2xl mr-3">👨‍🏫</div>
                    <div>
                      <h3 className="font-medium">Версия для учителя</h3>
                      <p className="text-sm text-gray-600">Задачи с ответами и решениями</p>
                    </div>
                  </div>
                  <button
                    onClick={() => downloadPDF('teacher')}
                    disabled={downloading.teacher}
                    className="w-full bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:opacity-50"
                  >
                    {downloading.teacher ? 'Скачивание...' : 'Скачать PDF учителя'}
                  </button>
                </div>
              </div>
            </div>

            {assignment.items && assignment.items.length > 0 && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-4">Список задач</h2>
                
                <div className="space-y-4">
                  {assignment.items.map((item, index) => (
                    <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="font-medium">
                          Задача {index + 1}: {item.task.topic}
                          {item.task.subtopic && ` - ${item.task.subtopic}`}
                        </h3>
                        <span className="text-sm bg-gray-100 px-2 py-1 rounded">
                          Сложность: {item.task.difficulty}/5
                        </span>
                      </div>
                      
                      <p className="text-gray-700 mb-2">
                        {item.task.statement_text.substring(0, 200)}
                        {item.task.statement_text.length > 200 && '...'}
                      </p>
                      
                      {item.selection_reason && (
                        <p className="text-sm text-blue-600">
                          <strong>Причина выбора:</strong> {item.selection_reason}
                        </p>
                      )}
                      
                      {item.rag_score && (
                        <p className="text-sm text-gray-500">
                          Релевантность: {(item.rag_score * 100).toFixed(1)}%
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default AssignmentResultPage;



