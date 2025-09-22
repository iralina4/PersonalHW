import React from 'react';
import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <div className="text-center">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          Персонализированная подготовка к ЕГЭ по математике
        </h1>
        
        <p className="text-xl text-gray-600 mb-12">
          Система автоматической генерации домашних заданий на основе профиля ученика 
          с использованием искусственного интеллекта и базы задач ЕГЭ
        </p>

        <div className="grid md:grid-cols-3 gap-8 mb-12">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl mb-4">👤</div>
            <h3 className="text-xl font-semibold mb-2">Профиль ученика</h3>
            <p className="text-gray-600 mb-4">
              Создайте детальный профиль с указанием слабых и сильных тем, 
              целевого балла и предпочтений
            </p>
            <Link 
              to="/student" 
              className="inline-block bg-primary-500 text-white px-4 py-2 rounded hover:bg-primary-600"
            >
              Создать профиль
            </Link>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl mb-4">🎯</div>
            <h3 className="text-xl font-semibold mb-2">Генерация заданий</h3>
            <p className="text-gray-600 mb-4">
              Укажите темы и количество задач, система подберет персонализированные 
              задания из базы
            </p>
            <Link 
              to="/generate" 
              className="inline-block bg-primary-500 text-white px-4 py-2 rounded hover:bg-primary-600"
            >
              Сгенерировать ДЗ
            </Link>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl mb-4">📄</div>
            <h3 className="text-xl font-semibold mb-2">PDF документы</h3>
            <p className="text-gray-600 mb-4">
              Получите готовые PDF файлы: вариант для ученика и вариант 
              с ответами для учителя
            </p>
            <button 
              className="bg-gray-300 text-gray-600 px-4 py-2 rounded cursor-not-allowed"
              disabled
            >
              Скачать PDF
            </button>
          </div>
        </div>

        <div className="bg-blue-50 p-6 rounded-lg">
          <h2 className="text-2xl font-semibold mb-4">Как это работает?</h2>
          <div className="grid md:grid-cols-4 gap-4 text-left">
            <div>
              <div className="bg-primary-500 text-white w-8 h-8 rounded-full flex items-center justify-center mb-2">1</div>
              <h4 className="font-semibold">Анализ профиля</h4>
              <p className="text-sm text-gray-600">Система изучает слабые и сильные стороны ученика</p>
            </div>
            <div>
              <div className="bg-primary-500 text-white w-8 h-8 rounded-full flex items-center justify-center mb-2">2</div>
              <h4 className="font-semibold">Поиск задач</h4>
              <p className="text-sm text-gray-600">RAG система находит подходящие задачи в базе</p>
            </div>
            <div>
              <div className="bg-primary-500 text-white w-8 h-8 rounded-full flex items-center justify-center mb-2">3</div>
              <h4 className="font-semibold">Персонализация</h4>
              <p className="text-sm text-gray-600">YaGPT адаптирует задачи под конкретного ученика</p>
            </div>
            <div>
              <div className="bg-primary-500 text-white w-8 h-8 rounded-full flex items-center justify-center mb-2">4</div>
              <h4 className="font-semibold">Генерация PDF</h4>
              <p className="text-sm text-gray-600">Создание красивых PDF документов с LaTeX</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;



