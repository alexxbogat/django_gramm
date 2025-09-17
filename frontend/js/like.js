document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.like-btn').forEach(function (button) {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const postId = this.dataset.postId;

            fetch(`/${postId}/like/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(res => res.json())
                .then(data => {
                    if (!data.error) {
                        const icon = this.querySelector('i');
                        const countSpan = this.querySelector('.like-count');

                        icon.className = data.liked ? 'fas fa-heart' : 'far fa-heart';
                        countSpan.textContent = data.likes_count;

                        this.classList.toggle('liked', data.liked);
                    }
                });
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}