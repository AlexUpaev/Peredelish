function showTable() {
    const selectedTable = document.getElementById('tableSelect').value;
    const tables = document.querySelectorAll('.table-container');

    tables.forEach(table => {
        table.style.display = 'none'; // Скрываем все таблицы
    });

    document.getElementById(selectedTable).style.display = 'block'; // Показываем выбранную таблицу
}
