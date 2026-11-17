/**
 * NEXUS SOCIAL - POSTS & FEED JAVASCRIPT
 * Real-time Post Creation, Likes, Comments, Image Previews, Edit/Delete
 */

let selectedImages = [];

// Handle image selection in compose form
function handleImageSelect(input) {
  const previewContainer = document.getElementById('composeImagePreviews');
  if (!previewContainer) return;

  const files = Array.from(input.files);
  files.forEach(file => {
    if (!file.type.startsWith('image/')) {
      showToast('Only image files are allowed.', 'error');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      showToast(`File ${file.name} is larger than 5MB.`, 'error');
      return;
    }

    selectedImages.push(file);

    const reader = new FileReader();
    reader.onload = (e) => {
      const idx = selectedImages.length - 1;
      const box = document.createElement('div');
      box.className = 'preview-thumb-box';
      box.id = `thumbBox-${idx}`;
      box.innerHTML = `
        <img src="${e.target.result}" alt="Preview">
        <button type="button" class="preview-remove-btn" onclick="removeSelectedImage(${idx})">
          <i class="fa-solid fa-xmark"></i>
        </button>
      `;
      previewContainer.appendChild(box);
    };
    reader.readAsDataURL(file);
  });

  input.value = ''; // Reset input to allow re-selecting same file
}

function removeSelectedImage(idx) {
  selectedImages.splice(idx, 1);
  const previewContainer = document.getElementById('composeImagePreviews');
  if (previewContainer) {
    previewContainer.innerHTML = '';
    selectedImages.forEach((file, i) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const box = document.createElement('div');
        box.className = 'preview-thumb-box';
        box.id = `thumbBox-${i}`;
        box.innerHTML = `
          <img src="${e.target.result}" alt="Preview">
          <button type="button" class="preview-remove-btn" onclick="removeSelectedImage(${i})">
            <i class="fa-solid fa-xmark"></i>
          </button>
        `;
        previewContainer.appendChild(box);
      };
      reader.readAsDataURL(file);
    });
  }
}

// Toggle Post Builder Drawers
function toggleComposeDrawer(type) {
  const pollDrawer = document.getElementById('composePollDrawer');
  const codeDrawer = document.getElementById('composeCodeDrawer');
  const badgeDrawer = document.getElementById('composeBadgeDrawer');
  const typeInput = document.getElementById('composePostType');

  // Hide all first
  if (pollDrawer) pollDrawer.style.display = 'none';
  if (codeDrawer) codeDrawer.style.display = 'none';
  if (badgeDrawer) badgeDrawer.style.display = 'none';

  if (!type || (typeInput && typeInput.value === type)) {
    if (typeInput) typeInput.value = 'standard';
    return;
  }

  if (typeInput) typeInput.value = type;

  if (type === 'poll' && pollDrawer) pollDrawer.style.display = 'block';
  if (type === 'code' && codeDrawer) codeDrawer.style.display = 'block';
  if (type === 'announcement' && badgeDrawer) badgeDrawer.style.display = 'block';
}

function addPollOptionField() {
  const container = document.getElementById('pollOptionsInputContainer');
  if (!container) return;
  const count = container.querySelectorAll('input').length;
  if (count >= 5) {
    showToast('Maximum 5 options per poll.', 'info');
    return;
  }
  const input = document.createElement('input');
  input.type = 'text';
  input.name = 'poll_options[]';
  input.className = 'form-control form-control-sm';
  input.placeholder = `Choice ${count + 1}`;
  input.style.cssText = 'background: var(--bg-surface); color: var(--text-primary); border-color: var(--border-subtle);';
  container.appendChild(input);
}

// Copy Code Snippet Helper
function copyCodeSnippet(buttonEl) {
  const preEl = buttonEl.closest('.code-snippet-box').querySelector('code');
  if (!preEl) return;
  navigator.clipboard.writeText(preEl.innerText).then(() => {
    const textSpan = buttonEl.querySelector('span');
    const icon = buttonEl.querySelector('i');
    if (textSpan) textSpan.textContent = 'Copied!';
    if (icon) icon.className = 'fa-solid fa-check text-success me-1';
    showToast('Code copied to clipboard!', 'success');
    setTimeout(() => {
      if (textSpan) textSpan.textContent = 'Copy';
      if (icon) icon.className = 'fa-regular fa-copy me-1';
    }, 2000);
  });
}

// Vote in Interactive Poll
async function votePoll(postId, optionId, buttonEl) {
  try {
    const fd = new FormData();
    fd.append('option_id', optionId);

    const res = await fetch(`/api/posts/${postId}/vote/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN },
      body: fd
    });

    const data = await res.json();
    if (data.success) {
      const container = document.getElementById(`pollOptionsList-${postId}`);
      if (container) {
        let html = '';
        data.options.forEach(opt => {
          const isVotedClass = opt.is_voted ? 'border-primary fw-bold' : '';
          const checkIcon = opt.is_voted ? '<i class="fa-solid fa-circle-check text-primary me-2"></i>' : '';
          html += `
            <button type="button" class="btn w-100 text-start position-relative overflow-hidden poll-opt-btn p-2 rounded-3 border-light-subtle ${isVotedClass}" onclick="votePoll(${postId}, ${opt.id}, this)" style="border: 1px solid var(--border-subtle); background: var(--bg-surface); color: var(--text-primary);">
              <div class="poll-bar-fill position-absolute top-0 start-0 bottom-0" style="width: ${opt.percentage}%; background: var(--primary-light); z-index: 1; transition: width 0.4s ease;"></div>
              <div class="position-relative d-flex justify-content-between align-items-center px-2 py-1" style="z-index: 2;">
                <span class="fw-medium">${checkIcon}${opt.text}</span>
                <span class="fw-bold small ms-2 text-muted poll-opt-pct">${opt.percentage}%</span>
              </div>
            </button>
          `;
        });
        container.innerHTML = html;
      }

      const totalSpan = document.getElementById(`pollTotalVotes-${postId}`);
      if (totalSpan) {
        totalSpan.textContent = `${data.total_votes} vote${data.total_votes === 1 ? '' : 's'}`;
      }

      showToast('Vote recorded!', 'success');
    } else {
      showToast(data.error || 'Failed to submit vote.', 'error');
    }
  } catch (err) {
    showToast('Network error while voting.', 'error');
  }
}

// Submit Create Post Form
async function submitCreatePost(event) {
  event.preventDefault();
  const form = event.target;
  const textarea = form.querySelector('textarea[name="content"]');
  const submitBtn = form.querySelector('button[type="submit"]');
  const content = textarea.value.trim();

  const postType = (form.querySelector('#composePostType') || {}).value || 'standard';
  const codeSnippet = (form.querySelector('textarea[name="code_snippet"]') || {}).value || '';
  const pollQuestion = (form.querySelector('input[name="poll_question"]') || {}).value || '';

  if (!content && selectedImages.length === 0 && !codeSnippet && !pollQuestion) {
    showToast('Please enter text, attach an image, or create a poll/code snippet.', 'error');
    return;
  }

  submitBtn.disabled = true;
  submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Posting...';

  const formData = new FormData(form);
  selectedImages.forEach(file => {
    formData.append('images', file);
  });

  try {
    const res = await fetch('/api/posts/create/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': CSRF_TOKEN
      },
      body: formData
    });

    const data = await res.json();
    if (data.success) {
      showToast('Post published successfully!', 'success');
      textarea.value = '';
      selectedImages = [];
      const previewContainer = document.getElementById('composeImagePreviews');
      if (previewContainer) previewContainer.innerHTML = '';
      
      // Reload current page to seamlessly show newest post
      setTimeout(() => {
        window.location.reload();
      }, 500);
    } else {
      showToast(data.error || 'Failed to create post.', 'error');
    }
  } catch (err) {
    showToast('Network error while publishing post.', 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = 'Post';
  }
}

// Like / Unlike Post
async function toggleLike(postId, buttonEl) {
  if (!buttonEl) return;
  buttonEl.disabled = true;

  const countSpan = buttonEl.querySelector('.like-count');
  const heartIcon = buttonEl.querySelector('i');

  try {
    const res = await fetch(`/api/posts/${postId}/like/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': CSRF_TOKEN,
        'Content-Type': 'application/json'
      }
    });

    const data = await res.json();
    if (data.success) {
      if (countSpan) countSpan.textContent = data.likes_count;

      if (data.liked) {
        buttonEl.classList.add('liked');
        heartIcon.className = 'fa-solid fa-heart';
        buttonEl.classList.add('animate-like');
        setTimeout(() => buttonEl.classList.remove('animate-like'), 400);
      } else {
        buttonEl.classList.remove('liked');
        heartIcon.className = 'fa-regular fa-heart';
      }
    }
  } catch (err) {
    showToast('Network error while liking post.', 'error');
  } finally {
    buttonEl.disabled = false;
  }
}

// Bookmark Post
async function toggleBookmark(postId, buttonEl) {
  if (!buttonEl) return;
  buttonEl.disabled = true;

  const icon = buttonEl.querySelector('i');

  try {
    const res = await fetch(`/api/posts/${postId}/bookmark/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': CSRF_TOKEN,
        'Content-Type': 'application/json'
      }
    });

    const data = await res.json();
    if (data.success) {
      if (data.bookmarked) {
        buttonEl.classList.add('saved');
        icon.className = 'fa-solid fa-bookmark';
        showToast('Post saved to bookmarks!', 'success');
      } else {
        buttonEl.classList.remove('saved');
        icon.className = 'fa-regular fa-bookmark';
        showToast('Post removed from bookmarks.', 'info');
      }
    }
  } catch (err) {
    showToast('Failed to update bookmark.', 'error');
  } finally {
    buttonEl.disabled = false;
  }
}

// Share Post Link
function sharePost(postUrl, fullTitle = 'Nexus Social Post') {
  const fullUrl = window.location.origin + postUrl;
  if (navigator.share) {
    navigator.share({
      title: fullTitle,
      url: fullUrl
    }).catch(() => {});
  } else {
    navigator.clipboard.writeText(fullUrl).then(() => {
      showToast('Post link copied to clipboard!', 'success');
    }).catch(() => {
      showToast('Failed to copy link.', 'error');
    });
  }
}

// Toggle comments drawer/list
function toggleComments(postId) {
  const container = document.getElementById(`commentsSection-${postId}`);
  if (container) {
    if (container.style.display === 'none' || !container.style.display) {
      container.style.display = 'block';
      const input = container.querySelector('input[name="content"]');
      if (input) input.focus();
    } else {
      container.style.display = 'none';
    }
  }
}

// Submit Comment
async function submitComment(event, postId) {
  event.preventDefault();
  const form = event.target;
  const input = form.querySelector('input[name="content"]');
  const parentInput = form.querySelector('input[name="parent_id"]');
  const content = input.value.trim();
  const parentId = parentInput ? parentInput.value : null;

  if (!content) return;

  const submitBtn = form.querySelector('button[type="submit"]');
  submitBtn.disabled = true;

  const formData = new FormData();
  formData.append('content', content);
  if (parentId) formData.append('parent_id', parentId);

  try {
    const res = await fetch(`/api/posts/${postId}/comments/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN },
      body: formData
    });

    const data = await res.json();
    if (data.success) {
      input.value = '';
      if (parentInput) parentInput.value = '';

      // Update comment count on post card
      const countEl = document.querySelector(`#postCard-${postId} .comment-count`);
      if (countEl) countEl.textContent = data.comments_count;

      // Append comment to list
      const listEl = document.getElementById(`commentsList-${postId}`);
      if (listEl) {
        const c = data.comment;
        const commentDiv = document.createElement('div');
        commentDiv.className = 'comment-item';
        commentDiv.id = `commentItem-${c.id}`;
        commentDiv.innerHTML = `
          <a href="/accounts/profile/${c.author}/">
            <img src="${c.author_avatar}" class="user-avatar-sm" alt="${c.author}">
          </a>
          <div class="comment-bubble">
            <div class="comment-header">
              <a href="/accounts/profile/${c.author}/" class="comment-author-name">
                ${c.author_name}
              </a>
              <div class="d-flex align-items-center gap-2">
                <span class="comment-time">${c.created_at}</span>
                <button type="button" class="btn btn-link btn-sm p-0 text-danger" onclick="deleteComment(${c.id}, ${postId})">
                  <i class="fa-solid fa-trash-can fa-xs"></i>
                </button>
              </div>
            </div>
            <div class="comment-text">${c.content}</div>
          </div>
        `;
        listEl.appendChild(commentDiv);
      }
      showToast('Comment posted.', 'success');
    } else {
      showToast(data.error || 'Failed to submit comment.', 'error');
    }
  } catch (err) {
    showToast('Error sending comment.', 'error');
  } finally {
    submitBtn.disabled = false;
  }
}

// Delete Comment
async function deleteComment(commentId, postId) {
  if (!confirm('Are you sure you want to delete this comment?')) return;

  try {
    const res = await fetch(`/api/comments/${commentId}/delete/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN }
    });

    const data = await res.json();
    if (data.success) {
      const el = document.getElementById(`commentItem-${commentId}`);
      if (el) el.remove();

      const countEl = document.querySelector(`#postCard-${postId} .comment-count`);
      if (countEl) countEl.textContent = data.comments_count;
      showToast('Comment deleted.', 'info');
    }
  } catch (e) {
    showToast('Failed to delete comment.', 'error');
  }
}

// Open Edit Post Modal
function openEditPostModal(postId, currentContent) {
  const modalEl = document.getElementById('nexusEditPostModal');
  const input = document.getElementById('editPostContentInput');
  const form = document.getElementById('editPostForm');
  if (!modalEl || !input || !form) return;

  input.value = currentContent;
  form.onsubmit = async (e) => {
    e.preventDefault();
    const newContent = input.value.trim();
    if (!newContent) return;

    const fd = new FormData();
    fd.append('content', newContent);

    try {
      const res = await fetch(`/api/posts/${postId}/edit/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': CSRF_TOKEN },
        body: fd
      });
      const data = await res.json();
      if (data.success) {
        const bodyEl = document.querySelector(`#postCard-${postId} .post-body`);
        if (bodyEl) bodyEl.innerHTML = data.formatted_content;
        bootstrap.Modal.getInstance(modalEl).hide();
        showToast('Post updated!', 'success');
      } else {
        showToast(data.error || 'Failed to edit post.', 'error');
      }
    } catch (err) {
      showToast('Network error while updating post.', 'error');
    }
  };

  const modal = new bootstrap.Modal(modalEl);
  modal.show();
}

// Delete Post
async function deletePost(postId) {
  if (!confirm('Are you sure you want to delete this post? This action cannot be undone.')) return;

  try {
    const res = await fetch(`/api/posts/${postId}/delete/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN }
    });

    const data = await res.json();
    if (data.success) {
      const card = document.getElementById(`postCard-${postId}`);
      if (card) {
        card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        card.style.opacity = '0';
        card.style.transform = 'translateY(-10px)';
        setTimeout(() => card.remove(), 300);
      }
      showToast('Post deleted.', 'info');
    } else {
      showToast(data.error || 'Unauthorized.', 'error');
    }
  } catch (err) {
    showToast('Error deleting post.', 'error');
  }
}

// Open Report Modal
function openReportModal(postId) {
  const modalEl = document.getElementById('nexusReportModal');
  const form = document.getElementById('nexusReportForm');
  if (!modalEl || !form) return;

  form.onsubmit = async (e) => {
    e.preventDefault();
    const reason = form.querySelector('select[name="reason"]').value;
    const details = form.querySelector('textarea[name="details"]').value;

    const fd = new FormData();
    fd.append('reason', reason);
    fd.append('details', details);

    try {
      const res = await fetch(`/api/posts/${postId}/report/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': CSRF_TOKEN },
        body: fd
      });
      const data = await res.json();
      if (data.success) {
        bootstrap.Modal.getInstance(modalEl).hide();
        showToast(data.message, 'success');
      } else {
        showToast(data.error || 'Failed to submit report.', 'error');
      }
    } catch (e) {
      showToast('Network error.', 'error');
    }
  };

  const modal = new bootstrap.Modal(modalEl);
  modal.show();
}

// Lightbox image viewer
function openLightbox(imgSrc) {
  const lightboxModal = document.getElementById('nexusLightboxModal');
  const imgEl = document.getElementById('lightboxModalImage');
  if (lightboxModal && imgEl) {
    imgEl.src = imgSrc;
    const modal = new bootstrap.Modal(lightboxModal);
    modal.show();
  }
}
