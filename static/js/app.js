/**
 * NEXUS SOCIAL - CORE CLIENT JAVASCRIPT
 * Theme switching, CSRF handling, Toasts, Follows, Notifications
 */

// Helper to get CSRF cookie
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const CSRF_TOKEN = getCookie('csrftoken');

// Toast Notification Manager
function showToast(message, type = 'info') {
  let container = document.getElementById('nexusToastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'nexusToastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = 'nexus-toast';
  
  let iconClass = 'fa-solid fa-circle-info text-primary';
  if (type === 'success') iconClass = 'fa-solid fa-circle-check text-success';
  if (type === 'error') iconClass = 'fa-solid fa-circle-exclamation text-danger';

  toast.innerHTML = `
    <i class="${iconClass}"></i>
    <span style="flex: 1; font-weight: 500;">${message}</span>
    <button type="button" style="background: none; border: none; color: var(--text-muted); cursor: pointer;" onclick="this.parentElement.remove()">
      <i class="fa-solid fa-xmark"></i>
    </button>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

// Theme (Dark / Light) Management
function initTheme() {
  const savedTheme = localStorage.getItem('nexus_theme') || 
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcons(savedTheme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const newTheme = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('nexus_theme', newTheme);
  updateThemeIcons(newTheme);
}

function updateThemeIcons(theme) {
  document.querySelectorAll('.theme-toggle-btn i').forEach(icon => {
    if (theme === 'dark') {
      icon.className = 'fa-solid fa-sun';
    } else {
      icon.className = 'fa-solid fa-moon';
    }
  });
}

// Global Follow / Unfollow Toggle
async function toggleFollow(username, buttonEl) {
  if (!buttonEl) return;
  buttonEl.disabled = true;

  try {
    const res = await fetch(`/api/users/${username}/follow/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': CSRF_TOKEN,
        'Content-Type': 'application/json'
      }
    });

    const data = await res.json();
    if (data.success) {
      if (data.is_following) {
        buttonEl.classList.add('following');
        buttonEl.innerHTML = '<i class="fa-solid fa-user-check"></i> Following';
        showToast(`You are now following @${username}`, 'success');
      } else {
        buttonEl.classList.remove('following');
        buttonEl.innerHTML = '<i class="fa-solid fa-user-plus"></i> Follow';
        showToast(`Unfollowed @${username}`, 'info');
      }

      // Update followers count if present on profile
      const followerCountEl = document.getElementById('profileFollowersCount');
      if (followerCountEl) {
        followerCountEl.textContent = data.followers_count;
      }
    } else {
      showToast(data.error || 'Failed to update follow status.', 'error');
    }
  } catch (err) {
    showToast('Network error while following user.', 'error');
  } finally {
    buttonEl.disabled = false;
  }
}

// Global Block / Unblock Toggle
async function toggleBlock(username, buttonEl) {
  if (!confirm(`Are you sure you want to block/unblock @${username}?`)) return;

  try {
    const res = await fetch(`/api/users/${username}/block/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN }
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.blocked ? `@${username} has been blocked.` : `@${username} has been unblocked.`, 'info');
      setTimeout(() => window.location.reload(), 1000);
    }
  } catch (e) {
    showToast('Failed to change block status.', 'error');
  }
}

// Global User List Modal (Followers, Following, Likes)
async function openUsersModal(title, fetchUrl) {
  const modalEl = document.getElementById('nexusUsersModal');
  const modalTitle = document.getElementById('nexusUsersModalTitle');
  const modalList = document.getElementById('nexusUsersModalList');

  if (!modalEl || !modalTitle || !modalList) return;

  modalTitle.textContent = title;
  modalList.innerHTML = '<div class="text-center py-4"><i class="fa-solid fa-spinner fa-spin fa-2x text-muted"></i></div>';

  const modal = new bootstrap.Modal(modalEl);
  modal.show();

  try {
    const res = await fetch(fetchUrl);
    const data = await res.json();
    const users = data.users || [];

    if (users.length === 0) {
      modalList.innerHTML = '<div class="text-center py-4 text-muted">No users found.</div>';
      return;
    }

    let html = '';
    users.forEach(u => {
      let actionBtn = '';
      if (!u.is_self) {
        const followClass = u.is_following ? 'btn-follow following' : 'btn-follow btn-primary-gradient';
        const followText = u.is_following ? 'Following' : 'Follow';
        actionBtn = `
          <button class="btn btn-sm ${followClass}" onclick="toggleFollow('${u.username}', this)">
            ${followText}
          </button>
        `;
      }

      html += `
        <div class="d-flex align-items-center justify-content-between py-2 border-bottom border-light-subtle">
          <div class="d-flex align-items-center gap-3">
            <a href="/accounts/profile/${u.username}/">
              <img src="${u.avatar_url}" class="user-avatar-sm" alt="${u.username}">
            </a>
            <div>
              <a href="/accounts/profile/${u.username}/" class="text-decoration-none fw-bold" style="color: var(--text-primary);">
                ${u.display_name}
              </a>
              <div class="text-muted small">@${u.username}</div>
            </div>
          </div>
          ${actionBtn}
        </div>
      `;
    });

    modalList.innerHTML = html;
  } catch (err) {
    modalList.innerHTML = '<div class="text-center py-3 text-danger">Failed to load users.</div>';
  }
}

// Notifications Helper
async function markNotificationRead(id, btnEl) {
  try {
    const res = await fetch(`/api/notifications/${id}/read/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN }
    });
    const data = await res.json();
    if (data.success) {
      const item = document.getElementById(`notificationItem-${id}`);
      if (item) {
        item.classList.remove('bg-subtle');
        item.style.opacity = '0.7';
      }
      updateNotificationBadges(data.unread_count);
    }
  } catch (e) {}
}

async function markAllNotificationsRead() {
  try {
    const res = await fetch('/api/notifications/mark-all-read/', {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN }
    });
    const data = await res.json();
    if (data.success) {
      document.querySelectorAll('.notification-unread-dot').forEach(dot => dot.remove());
      updateNotificationBadges(0);
      showToast('All notifications marked as read.', 'success');
    }
  } catch (e) {
    showToast('Failed to mark all as read.', 'error');
  }
}

function updateNotificationBadges(count) {
  document.querySelectorAll('.notification-badge').forEach(badge => {
    if (count > 0) {
      badge.textContent = count;
      badge.style.display = 'inline-block';
    } else {
      badge.style.display = 'none';
    }
  });
}

// Initializer
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
});
