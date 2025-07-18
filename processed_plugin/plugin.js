/**
 * Барбершоп календарь-бот плагин
 * Встраиваемый виджет для сайта
 */

(function() {
    'use strict';
    
    // Конфигурация из JALM
    window.BARBERS = [{"name": "Илья", "tg_id": "@ilya_barber", "photo": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=150&h=150&fit=crop&crop=face", "speciality": "barber", "experience": "5 лет", "rating": "4.9"}, {"name": "Мария", "tg_id": "@mary_barber", "photo": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face", "speciality": "colorist", "experience": "3 года", "rating": "4.8"}, {"name": "Алексей", "tg_id": "@alex_barber", "photo": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face", "speciality": "barber", "experience": "7 лет", "rating": "4.9"}, {"name": "Елена", "tg_id": "@elena_barber", "photo": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face", "speciality": "stylist", "experience": "4 года", "rating": "4.7"}, {"name": "Дмитрий", "tg_id": "@dmitry_barber", "photo": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face", "speciality": "barber", "experience": "6 лет", "rating": "4.8 "}];
    window.CHATBOT_URL = 'https://t.me/demo_barbershop_001_bot';
    window.SHOP_NAME = 'Барбершоп 'Классика'';
    window.PRIMARY_COLOR = '#2C3E50';
    
    // Создание виджета
    function createBookingWidget() {
        const widget = document.createElement('div');
        widget.id = 'barbershop-booking-widget';
        widget.innerHTML = `
            <style>
                .booking-widget {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 10000;
                    font-family: 'Arial', sans-serif;
                }
                .booking-button {
                    background: ${window.PRIMARY_COLOR};
                    color: white;
                    border: none;
                    border-radius: 50px;
                    padding: 15px 25px;
                    font-size: 16px;
                    cursor: pointer;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    transition: all 0.3s ease;
                }
                .booking-button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(0,0,0,0.2);
                }
                .booking-modal {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.5);
                    z-index: 10001;
                    display: none;
                }
                .modal-content {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    max-width: 400px;
                    width: 90%;
                }
                .barber-list {
                    margin: 20px 0;
                }
                .barber-item {
                    display: flex;
                    align-items: center;
                    padding: 10px;
                    border: 1px solid #eee;
                    margin: 5px 0;
                    border-radius: 5px;
                    cursor: pointer;
                }
                .barber-item:hover {
                    background: #f5f5f5;
                }
                .barber-photo {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    margin-right: 10px;
                }
                .close-modal {
                    position: absolute;
                    top: 10px;
                    right: 15px;
                    font-size: 24px;
                    cursor: pointer;
                    color: #999;
                }
            </style>
            
            <div class="booking-widget">
                <button class="booking-button" onclick="openBookingModal()">
                    ✂️ Записаться к барберу
                </button>
            </div>
            
            <div class="booking-modal" id="bookingModal">
                <div class="modal-content">
                    <span class="close-modal" onclick="closeBookingModal()">&times;</span>
                    <h2>${window.SHOP_NAME}</h2>
                    <p>Выберите барбера для записи:</p>
                    
                    <div class="barber-list" id="barberList">
                        ${generateBarberList()}
                    </div>
                    
                    <button onclick="openTelegramChat()" style="
                        background: #0088cc;
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 5px;
                        cursor: pointer;
                        width: 100%;
                        margin-top: 20px;
                    ">
                        💬 Открыть чат в Telegram
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(widget);
    }
    
    function generateBarberList() {
        return window.BARBERS.map(barber => `
            <div class="barber-item" onclick="selectBarber('${barber.name}', '${barber.tg_id}')">
                <img src="${barber.photo}" alt="${barber.name}" class="barber-photo">
                <div>
                    <strong>${barber.name}</strong><br>
                    <small>${barber.speciality}</small>
                </div>
            </div>
        `).join('');
    }
    
    // Глобальные функции
    window.openBookingModal = function() {
        document.getElementById('bookingModal').style.display = 'block';
    };
    
    window.closeBookingModal = function() {
        document.getElementById('bookingModal').style.display = 'none';
    };
    
    window.selectBarber = function(name, tgId) {
        // Отправляем данные в Telegram бота
        const message = `Хочу записаться к ${name} (@${tgId})`;
        window.openTelegramChat(message);
        closeBookingModal();
    };
    
    window.openTelegramChat = function(message = '') {
        const url = message ? 
            `${window.CHATBOT_URL}?start=${encodeURIComponent(message)}` :
            window.CHATBOT_URL;
        window.open(url, '_blank');
    };
    
    // Закрытие модального окна при клике вне его
    document.addEventListener('click', function(event) {
        const modal = document.getElementById('bookingModal');
        if (event.target === modal) {
            closeBookingModal();
        }
    });
    
    // Инициализация при загрузке страницы
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createBookingWidget);
    } else {
        createBookingWidget();
    }
    
})(); 