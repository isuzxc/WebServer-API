$(document).ready(function() {
    // При отправке формы добавления транзакции
    $('#addTransactionForm').submit(function(event) {
        event.preventDefault();
        var formData = {
            description: $('#description').val(),
            amount: parseFloat($('#amount').val())
        };
        $.ajax({
            type: 'POST',
            url: '/api/transactions',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function(response) {
                alert(response.message);
                loadTransactions();
            },
            error: function(xhr, status, error) {
                alert('Error adding transaction');
            }
        });
    });

    // Функция загрузки списка транзакций
    function loadTransactions() {
        $.get('/api/transactions', function(data) {
            var transactionList = $('#transactionList');
            transactionList.empty();
            data.forEach(function(transaction) {
                transactionList.append(`<p><strong>${transaction.description}</strong>: $${transaction.amount} (${transaction.date})</p>`);
            });
        });
    }

    // Инициализация загрузки списка транзакций при загрузке страницы
    loadTransactions();
});
