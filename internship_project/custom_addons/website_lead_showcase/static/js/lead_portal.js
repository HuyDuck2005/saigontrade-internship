document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('lead_contact_form');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactSubmit);
    }
});

async function handleContactSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const parts = window.location.pathname.split('/');
    const leadId = parts[parts.length - 1];
    
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Đang gửi...';
    
    try {
        const formData = new FormData(form);
        const response = await fetch(`/leads/${leadId}/contact`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        const statusDiv = document.getElementById('form_status_message');
        
        if (result.status === 'success') {
            statusDiv.innerHTML = `<div class="alert alert-success mt-3">${result.message}</div>`;
            form.reset();
        } else {
            statusDiv.innerHTML = `<div class="alert alert-danger mt-3">${result.message}</div>`;
        }
    } catch (error) {
        document.getElementById('form_status_message').innerHTML = `
            <div class="alert alert-danger mt-3">Lỗi kết nối. Vui lòng tải lại trang và thử lại!</div>`;
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}
