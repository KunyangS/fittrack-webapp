document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form[action="#"]');
    const input = document.getElementById('share-with-users');
    const errorAlert = document.getElementById('share-form-error');
    const errorMsg = document.getElementById('share-form-error-msg');
    const categoryCheckboxes = document.querySelectorAll('input[name="share_options"]');
    // Assuming 'messages' is not available in JS, this logic might need adjustment
    // or 'messages' should be passed to the script if needed.
    // For now, we'll assume hasFlashMessages is determined differently or not used directly in JS.
    // const hasFlashMessages = {{ messages|length > 0 | tojson }}; 
    // This line ^^^ cannot be directly translated to a separate JS file without passing the value.
    // For the purpose of this extraction, I will assume hasFlashMessages functionality
    // will be handled by checking if the errorAlert div has backend-generated content.
    const hasFlashMessages = errorAlert && !errorAlert.classList.contains('hidden') && errorMsg.textContent.trim() !== '';


    if (form && input && errorAlert && errorMsg && categoryCheckboxes.length) {
      form.addEventListener('submit', function(e) {
        const recipientUsername = input.value.trim();
        let confirmMessage;

        if (recipientUsername) {
          confirmMessage = `Are you sure you want to share data with ${recipientUsername}?`;
        } else {
          confirmMessage = 'Are you sure you want to proceed with granting sharing access?';
        }

        if (!confirm(confirmMessage)) {
          e.preventDefault(); 
          return;
        }
        
        // Check if the error alert is visible and contains a message not set by frontend validation
        // This is a proxy for hasFlashMessages
        const backendErrorMessageVisible = !errorAlert.classList.contains('hidden') && 
                                           errorMsg.textContent.trim() !== '' &&
                                           !errorMsg.textContent.includes('Please enter at least one recipient.') &&
                                           !errorMsg.textContent.includes('Please select at least one data category.');

        if (!backendErrorMessageVisible) {
          let valid = true;
          let errorMessages = [];
          
          if (!input.value.trim()) {
            errorMessages.push('Please enter at least one recipient.');
            valid = false;
          }
          
          let checked = false;
          categoryCheckboxes.forEach(function(box) {
            if (box.checked) checked = true;
          });
          
          if (!checked) {
            errorMessages.push('Please select at least one data category.');
            valid = false;
          }
          
          if (!valid) {
            e.preventDefault();
            errorMsg.textContent = errorMessages.join(' ');
            errorAlert.classList.remove('hidden');
            errorAlert.classList.remove('bg-green-500','bg-yellow-400','text-gray-800');
            errorAlert.classList.add('bg-red-500','text-white');
            errorAlert.scrollIntoView({behavior: 'smooth', block: 'center'});
          } else {
            errorAlert.classList.add('hidden');
          }
        }
      });
      
      input.addEventListener('input', function() {
        const backendErrorMessageVisible = !errorAlert.classList.contains('hidden') &&
                                           errorMsg.textContent.trim() !== '' &&
                                           !errorMsg.textContent.includes('Please enter at least one recipient.') &&
                                           !errorMsg.textContent.includes('Please select at least one data category.');
        if (!backendErrorMessageVisible && input.value.trim()) {
          const currentError = errorMsg.textContent;
          if (currentError.includes('recipient') && !currentError.includes('data category')) {
            errorAlert.classList.add('hidden');
          }
        }
      });
      
      categoryCheckboxes.forEach(function(box) {
        box.addEventListener('change', function() {
          const backendErrorMessageVisible = !errorAlert.classList.contains('hidden') &&
                                             errorMsg.textContent.trim() !== '' &&
                                             !errorMsg.textContent.includes('Please enter at least one recipient.') &&
                                             !errorMsg.textContent.includes('Please select at least one data category.');
          if (!backendErrorMessageVisible) {
            let checked = false;
            categoryCheckboxes.forEach(function(b) { if (b.checked) checked = true; });
            
            if (checked) {
              const currentError = errorMsg.textContent;
              if (currentError.includes('data category') && !currentError.includes('recipient')) {
                errorAlert.classList.add('hidden');
              }
            }
          }
        });
      });
    }

    const revokeForms = document.querySelectorAll('form[action*="revoke_share"]');
    revokeForms.forEach(revokeForm => {
      revokeForm.addEventListener('submit', function(e) {
        const shareeNameElement = revokeForm.closest('.bg-white').querySelector('.text-primary');
        let shareeName = 'this user';
        if (shareeNameElement && shareeNameElement.textContent) {
          shareeName = shareeNameElement.textContent.trim();
        }
        if (!confirm(`Are you sure you want to revoke sharing with ${shareeName}?`)) {
          e.preventDefault();
        }
      });
    });
  });