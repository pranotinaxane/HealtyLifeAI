// Healthy Life AI Recommendation System - Client side interactions

document.addEventListener('DOMContentLoaded', function() {
    // 1. Mobile Menu Toggle Navigation
    const menuToggle = document.getElementById('menu-toggle');
    const navMenu = document.getElementById('nav-menu');
    
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('show');
            // Animate toggle lines
            const spans = menuToggle.querySelectorAll('span');
            spans[0].style.transform = navMenu.classList.contains('show') ? 'rotate(45deg) translate(5px, 5px)' : 'none';
            spans[1].style.opacity = navMenu.classList.contains('show') ? '0' : '1';
            spans[2].style.transform = navMenu.classList.contains('show') ? 'rotate(-45deg) translate(6px, -6px)' : 'none';
        });
    }

    // 2. Auto Dismiss Toasts
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        // Dismiss toast after 5 seconds
        setTimeout(() => {
            toast.classList.remove('show');
        }, 5000);
        
        // Manual close trigger
        const closeBtn = toast.querySelector('.toast-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                toast.classList.remove('show');
            });
        }
        
        toast.addEventListener('click', () => {
            toast.classList.remove('show');
        });
    });

    // 3. BMI Interactive Gauge Setup (if exists on page)
    const bmiIndicator = document.getElementById('bmi-indicator');
    if (bmiIndicator) {
        const bmiVal = parseFloat(bmiIndicator.dataset.bmi);
        if (!isNaN(bmiVal)) {
            // Map BMI from 15 (0%) to 35 (100%)
            let percent = ((bmiVal - 15) / (35 - 15)) * 100;
            // Bound it between 2% and 98% to avoid leaking off edges
            percent = Math.max(2, Math.min(98, percent));
            bmiIndicator.style.left = percent + '%';
        }
    }

    // 4. Interactive BMI Calculator Form (If exists on BMI Page)
    const calcForm = document.getElementById('bmi-calc-form');
    if (calcForm) {
        const calcWeight = document.getElementById('calc-weight');
        const calcHeight = document.getElementById('calc-height');
        const calcResultDiv = document.getElementById('calc-result-box');
        const calcBmiVal = document.getElementById('calc-bmi-value');
        const calcBmiCat = document.getElementById('calc-bmi-category');
        const calcBmiText = document.getElementById('calc-bmi-text');
        
        function calculateBmiRealtime() {
            const w = parseFloat(calcWeight.value);
            const hCm = parseFloat(calcHeight.value);
            
            if (w > 0 && hCm > 0) {
                const hM = hCm / 100.0;
                const bmi = w / (hM * hM);
                const roundedBmi = bmi.toFixed(2);
                
                let category = "";
                let badgeClass = "";
                let message = "";
                
                if (bmi < 18.5) {
                    category = "Underweight";
                    badgeClass = "badge-underweight";
                    message = "We recommend focusing on a nutritious calorie-surplus diet and mild strength training to gain lean muscle.";
                } else if (bmi >= 18.5 && bmi < 25) {
                    category = "Normal Weight";
                    badgeClass = "badge-normal";
                    message = "Fantastic! You are in the healthy zone. Focus on balanced nutrition and regular physical activity to maintain it.";
                } else if (bmi >= 25 && bmi < 30) {
                    category = "Overweight";
                    badgeClass = "badge-overweight";
                    message = "You are slightly above the healthy range. A balanced calorie-deficit diet and daily cardiovascular exercise will help you.";
                } else {
                    category = "Obese";
                    badgeClass = "badge-obese";
                    message = "Your BMI is in the high range. We strongly recommend consults with experts, structured aerobic workouts, and dietary shifts.";
                }
                
                calcBmiVal.textContent = roundedBmi;
                calcBmiCat.textContent = category;
                calcBmiCat.className = 'badge badge-bmi ' + badgeClass;
                calcBmiText.textContent = message;
                calcResultDiv.style.display = 'block';
                
                // Update slider gauge if present in the calculator results
                const calcBmiIndicator = document.getElementById('calc-bmi-indicator');
                if (calcBmiIndicator) {
                    let percent = ((bmi - 15) / (35 - 15)) * 100;
                    percent = Math.max(2, Math.min(98, percent));
                    calcBmiIndicator.style.left = percent + '%';
                }
            } else {
                calcResultDiv.style.display = 'none';
            }
        }
        
        calcWeight.addEventListener('input', calculateBmiRealtime);
        calcHeight.addEventListener('input', calculateBmiRealtime);
    }
});
