function highlightMatches(query) {
    const table = document.querySelector('.table tbody');
    const rows = table.getElementsByTagName('tr');

    // Убираем предыдущую подсветку
    for (let i = 0; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        for (let j = 0; j < cells.length; j++) {
            // Сбрасываем содержимое, если это не кнопка
            if (!cells[j].querySelector('button')) {
                cells[j].innerHTML = cells[j].textContent; 
            }
        }
    }

    if (query) {
        const regex = new RegExp(`(${query})`, 'gi'); // Регулярное выражение для поиска

        for (let i = 0; i < rows.length; i++) {
            const cells = rows[i].getElementsByTagName('td');
            for (let j = 0; j < cells.length; j++) {
                const cellText = cells[j].textContent;
                // Проверяем, не является ли ячейка кнопкой
                if (cellText.match(regex) && !cells[j].querySelector('button')) {
                    // Подсвечиваем совпадения
                    const highlightedText = cellText.replace(regex, '<span class="highlighted">\$1</span>');
                    cells[j].innerHTML = highlightedText;
                }
            }
        }
    }
}
