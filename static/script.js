let currentPage = 1;
let totalPages = 1;

document.addEventListener('DOMContentLoaded', function () {
    loadPage(currentPage);

    document.getElementById('prev-btn').addEventListener('click', function () {
        if (currentPage > 1) {
            currentPage--;
            loadPage(currentPage);
        }
    });

    document.getElementById('next-btn').addEventListener('click', function () {
        if (currentPage < totalPages) {
            currentPage++;
            loadPage(currentPage);
        }
    });
});

function loadPage(page) {
    fetch(`/get_data?page=${page}`)
        .then(response => response.json())
        .then(data => {
            const itemsDiv = document.getElementById('items');
            itemsDiv.innerHTML = '';
            data.items.forEach(item => {
                const div = document.createElement('div');
                div.textContent = item;
                itemsDiv.appendChild(div);
            });
            totalPages = data.total_pages;
            document.getElementById('page-info').textContent = `Page ${page} of ${totalPages}`;
        });
}
