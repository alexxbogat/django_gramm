document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.follow-form').forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        const btn = this.querySelector('button');
                        btn.textContent = data.following ? 'Unsubscribe' : 'Subscribe';
                        btn.classList.toggle('unfollow', data.following);

                        const profileStats = this.closest('.profile-info').querySelector('.profile-stats');
                        if (profileStats) {
                            const followersStat = profileStats.querySelectorAll('.stat')[0];
                            const followersCount = followersStat.querySelector('.stat-count');
                            followersCount.textContent = data.followers_count;
                        }
                    }
                });
        });
    });
});
