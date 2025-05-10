// Toggle Password Visibility
function togglePassword(el) {
    const input = el.previousElementSibling;
    if (input.type === "password") {
      input.type = "text";
      el.classList.remove("fa-eye");
      el.classList.add("fa-eye-slash");
    } else {
      input.type = "password";
      el.classList.remove("fa-eye-slash");
      el.classList.add("fa-eye");
    }
}

// Modal Open/Close for Terms and Conditions
document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("termsModal");
  const trigger = document.querySelector("[data-modal-trigger]");
  const closeBtn = document.getElementById("closeModal");

  if (trigger && modal && closeBtn) {
    trigger.addEventListener("click", function (e) {
      e.preventDefault();
      modal.classList.remove("hidden");
      modal.classList.add("flex");
    });

    closeBtn.addEventListener("click", function () {
      modal.classList.remove("flex");
      modal.classList.add("hidden");
    });

    window.addEventListener("click", function (e) {
      if (e.target === modal) {
        modal.classList.remove("flex");
        modal.classList.add("hidden");
      }
    });
  }

  // Password Strength Indicator
  const passwordInput = document.getElementById("password");
  if (passwordInput) {
    passwordInput.addEventListener("input", function () {
      checkPasswordStrength(passwordInput.value);
    });
  }
});

// Password Strength Checker
function checkPasswordStrength(password) {
  const strengthDisplay = document.getElementById("password-strength");
  // Adjust regex to match your backend requirements
 const strongRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_\-+=\[\]{}|;':",.<>/?~`]).{8,}$/;

  if (!strengthDisplay) return;

  if (password.length === 0) {
    strengthDisplay.textContent = "";
  } else if (strongRegex.test(password)) {
    strengthDisplay.textContent = "Strong password";
    strengthDisplay.style.color = "green";
  } else {
    strengthDisplay.textContent = "Weak password – use at least 8 chars, 1 uppercase, 1 digit, 1 special";
    strengthDisplay.style.color = "red";
  }
}

// Countdown Timer for Code Expiry (Verify Code Page)
if (document.getElementById('timer')) {
  let countdownTime = 120; // 2 minutes
  const timerDisplay = document.getElementById('timer');

  setInterval(() => {
    if (countdownTime > 0) {
      countdownTime--;
      const minutes = String(Math.floor(countdownTime / 60)).padStart(2, '0');
      const seconds = String(countdownTime % 60).padStart(2, '0');
      timerDisplay.textContent = `${minutes}:${seconds}`;
    }
  }, 1000);
}

// Resend Code Cooldown (Verify Code Page)
if (document.getElementById('resendBtn')) {
  let resendCooldown = 30;
  const resendBtn = document.getElementById('resendBtn');

  const resendInterval = setInterval(() => {
    if (resendCooldown > 0) {
      resendBtn.textContent = `Resend Code (${resendCooldown})`;
      resendCooldown--;
    } else {
      resendBtn.disabled = false;
      resendBtn.textContent = "Resend Code";
      clearInterval(resendInterval);
    }
  }, 1000);
}