function handleStatusChange(postId) {
    const selectElement = document.getElementById(`status-${postId}`);
    if (selectElement.value === 'Обнаружен' && !selectElement.dataset.triggered) {
        selectElement.dataset.triggered = true;
        openModal();  // Показываем модальное окно, если статус - "Обнаружен"
    }
    document.getElementById(`status-form-${postId}`).submit();  // Отправка формы
}
