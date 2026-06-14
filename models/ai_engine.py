import random

# Try importing scikit-learn
try:
    from sklearn.tree import DecisionTreeClassifier
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# Mapping Constants
GOAL_MAPPING = {
    'Weight Loss': 0,
    'Maintain Fitness': 1,
    'Weight Gain': 2
}

ACTIVITY_MAPPING = {
    'Sedentary': 0,
    'Lightly Active': 1,
    'Moderately Active': 2,
    'Very Active': 3
}

GENDER_MAPPING = {
    'Male': 0,
    'Female': 1,
    'Other': 2
}

class AIRecommendationEngine:
    def __init__(self):
        self.diet_model = None
        self.exercise_model = None
        self.trained = False
        
        if HAS_SKLEARN:
            try:
                self._train_models()
            except Exception as e:
                print(f"AI ENGINE WARNING: Failed to train Scikit-learn models: {e}. Falling back to Rule-Based system.")
                self.trained = False
        else:
            print("AI ENGINE WARNING: Scikit-learn not available. Falling back to Rule-Based system.")

    def _generate_synthetic_data(self, size=250):
        """Generates synthetic dataset to train the Decision Tree."""
        X = []
        y_diet = []
        y_exercise = []
        
        for _ in range(size):
            age = random.randint(15, 80)
            bmi = round(random.uniform(14.0, 40.0), 1)
            goal_str = random.choice(list(GOAL_MAPPING.keys()))
            activity_str = random.choice(list(ACTIVITY_MAPPING.keys()))
            
            goal_enc = GOAL_MAPPING[goal_str]
            activity_enc = ACTIVITY_MAPPING[activity_str]
            
            # 1. Rule-based Labeling for Diet Category
            # 0: Weight Gain (Calorie Surplus), 1: Maintain (Balanced), 2: Weight Loss (Calorie Deficit)
            if bmi < 18.5:
                diet_cat = 0
            elif bmi >= 25.0:
                diet_cat = 2
            else: # Normal weight
                if goal_str == 'Weight Gain':
                    diet_cat = 0
                elif goal_str == 'Weight Loss':
                    diet_cat = 2
                else:
                    diet_cat = 1
                    
            # 2. Rule-based Labeling for Exercise Intensity Category
            # 0: Light Yoga / Walking, 1: Moderate Cardio / Fitness, 2: High Intensity Gym / Strength
            if age > 60 or bmi > 32.0 or activity_str == 'Sedentary':
                exercise_cat = 0
            elif goal_str == 'Weight Gain' and age <= 45 and activity_str in ['Moderately Active', 'Very Active']:
                exercise_cat = 2
            elif goal_str == 'Weight Loss' or activity_str in ['Moderately Active', 'Very Active']:
                exercise_cat = 1
            else:
                exercise_cat = 0
                
            X.append([age, bmi, goal_enc, activity_enc])
            y_diet.append(diet_cat)
            y_exercise.append(exercise_cat)
            
        return np.array(X), np.array(y_diet), np.array(y_exercise)

    def _train_models(self):
        """Trains the Decision Tree Classifiers."""
        X, y_diet, y_exercise = self._generate_synthetic_data()
        
        self.diet_model = DecisionTreeClassifier(max_depth=4, random_state=42)
        self.diet_model.fit(X, y_diet)
        
        self.exercise_model = DecisionTreeClassifier(max_depth=4, random_state=42)
        self.exercise_model.fit(X, y_exercise)
        self.trained = True
        print("AI ENGINE STATUS: Scikit-learn Decision Tree models trained successfully.")

    def predict_categories(self, age, bmi, goal, activity_level):
        """Predicts diet and exercise categories using the model or fallback rules."""
        goal_enc = GOAL_MAPPING.get(goal, 1)
        activity_enc = ACTIVITY_MAPPING.get(activity_level, 1)
        
        if HAS_SKLEARN and self.trained:
            try:
                features = np.array([[age, bmi, goal_enc, activity_enc]])
                diet_cat = int(self.diet_model.predict(features)[0])
                exercise_cat = int(self.exercise_model.predict(features)[0])
                return diet_cat, exercise_cat, "Machine Learning Model (Decision Tree)"
            except Exception as e:
                print(f"AI Engine inference failed: {e}. Using rule fallback.")
                
        # Pure Python Fallback Rules
        # Diet fallback
        if bmi < 18.5:
            diet_cat = 0 # Weight Gain
        elif bmi >= 25.0:
            diet_cat = 2 # Weight Loss
        else:
            if goal == 'Weight Gain':
                diet_cat = 0
            elif goal == 'Weight Loss':
                diet_cat = 2
            else:
                diet_cat = 1 # Maintain
                
        # Exercise fallback
        if age > 60 or bmi > 32.0 or activity_level == 'Sedentary':
            exercise_cat = 0 # Light
        elif goal == 'Weight Gain' and age <= 45 and activity_level in ['Moderately Active', 'Very Active']:
            exercise_cat = 2 # High / Strength
        elif goal == 'Weight Loss' or activity_level in ['Moderately Active', 'Very Active']:
            exercise_cat = 1 # Moderate / Cardio
        else:
            exercise_cat = 0 # Light
            
        return diet_cat, exercise_cat, "Deterministic Rule-Based Logic"

    def get_recommendations(self, age, gender, height, weight, activity_level, goal):
        """Generates a complete, tailored health plan based on predicted classifications."""
        # Calculate BMI
        # height in cm, convert to meters
        height_m = height / 100.0
        bmi = weight / (height_m * height_m)
        bmi = round(bmi, 2)
        
        if bmi < 18.5:
            bmi_category = "Underweight"
        elif 18.5 <= bmi < 25.0:
            bmi_category = "Normal"
        elif 25.0 <= bmi < 30.0:
            bmi_category = "Overweight"
        else:
            bmi_category = "Obese"
            
        # Get AI Classifications
        diet_cat, exercise_cat, engine_source = self.predict_categories(age, bmi, goal, activity_level)
        
        # 1. DIET PLANS (Indian Simple Foods)
        diet_plans = {
            0: { # Weight Gain Diet (Calorie Surplus: ~2600-2800 kcal)
                'title': 'High-Calorie Nutritious Diet',
                'target_calories': '2,600 - 2,800 kcal',
                'macronutrients': 'Carbohydrates: 50%, Proteins: 25%, Fats: 25%',
                'meals': {
                    'breakfast': 'Stuffed Paneer Paratha (2 pcs) with curd or 3 boiled eggs + Oatmeal with bananas, almonds, and full cream milk.',
                    'lunch': '1 large bowl of brown rice, 3 Chapatis with ghee, 1 cup Thick Dal, 1 cup Paneer Bhurji / Chicken Curry, and green salad.',
                    'evening': 'Peanut butter sandwich on whole wheat bread, a handful of mixed dry fruits (cashews, raisins, walnuts) + Milkshake.',
                    'dinner': '3 Chapatis or Rice, 1 cup Mix Veg / Soya chunks, 1 cup Fish Curry or Dal Tadka, and a glass of warm milk at bedtime.'
                },
                'dietary_tips': [
                    'Eat calorie-dense foods like ghee, nuts, paneer, and bananas.',
                    'Eat every 3-4 hours and avoid drinking water immediately before meals.',
                    'Incorporate protein shakes or smoothies between meals.'
                ]
            },
            1: { # Maintain Diet (Balanced Diet: ~2000-2200 kcal)
                'title': 'Balanced Health & Vitality Diet',
                'target_calories': '2,000 - 2,200 kcal',
                'macronutrients': 'Carbohydrates: 55%, Proteins: 20%, Fats: 25%',
                'meals': {
                    'breakfast': 'Vegetable Oats Upma or Idli (3 pcs) with Sambar and coconut chutney + 1 cup green tea or skimmed milk.',
                    'lunch': '2 Chapatis, 1 small bowl of rice, 1 cup Moong Dal, 1 cup Seasonal Vegetable Sabzi (e.g., Bhindi, Gobhi), and 1 cup Curd.',
                    'evening': '1 cup roasted Makhana (foxnuts) or boiled Chana Chaat + a cup of green tea or filter coffee.',
                    'dinner': '2 Chapatis, 1 cup Grilled Paneer or Chicken breast, 1 cup stir-fried vegetables (broccoli, bell peppers, carrots).'
                },
                'dietary_tips': [
                    'Focus on variety: make sure your plate has diverse colors.',
                    'Keep refined sugars and processed flours (maida) to a minimum.',
                    'Use healthy cooking oils like mustard, olive, or groundnut oil in moderation.'
                ]
            },
            2: { # Weight Loss Diet (Calorie Deficit: ~1400-1600 kcal)
                'title': 'High-Protein Calorie Deficit Diet',
                'target_calories': '1,400 - 1,600 kcal',
                'macronutrients': 'Carbohydrates: 40%, Proteins: 35%, Fats: 25%',
                'meals': {
                    'breakfast': 'Moong Dal Cheela (2 pcs) filled with grated paneer, or 3 egg white omelet with spinach and tomatoes + 1 cup green tea.',
                    'lunch': '1 Chapati (Multigrain), 1 huge bowl of Dal (no oil tempering), 1 bowl of Boiled Soya Chunks or Chicken breast, and Cucumber-Tomato Salad.',
                    'evening': '1 sliced apple with 1 tbsp peanut butter or a bowl of sprouts salad with lemon juice.',
                    'dinner': 'Bowl of mixed vegetable soup + grilled paneer/tofu (100g) or steamed fish with sautéed broccoli and mushrooms.'
                },
                'dietary_tips': [
                    'Consume fiber-rich foods to keep you full longer.',
                    'Drink a glass of water 30 minutes before your meal to naturally reduce portion size.',
                    'Avoid sweet snacks and replace them with fresh fruits.'
                ]
            }
        }
        
        # 2. EXERCISE PLANS
        exercise_plans = {
            0: { # Light Yoga / Walking (Low Intensity)
                'title': 'Restorative & Light Movement Routine',
                'description': 'Designed for beginners, seniors, or recovery phases. Focuses on joint mobility, flexibility, and light cardio.',
                'frequency': '4-5 days a week',
                'duration': '30-40 minutes',
                'exercises': [
                    {'name': 'Brisk Walking', 'sets': '1 session', 'reps': '20-30 mins', 'benefit': 'Improves cardiovascular circulation.'},
                    {'name': 'Pranayama (Deep Breathing)', 'sets': '3 rounds', 'reps': '5 mins', 'benefit': 'Relieves stress and improves lung capacity.'},
                    {'name': 'Surya Namaskar (Sun Salutations)', 'sets': '3-5 rounds', 'reps': 'Slow pace', 'benefit': 'Improves overall flexibility.'},
                    {'name': 'Neck & Shoulder Rolls, Ankle Rotations', 'sets': '2 sets', 'reps': '10 reps each', 'benefit': 'Reduces joint stiffness.'}
                ],
                'precaution': 'Listen to your body. Do not overstretch or push into sharp joint pain.'
            },
            1: { # Moderate Cardio & Fitness
                'title': 'Active Heart & Core Cardio Routine',
                'description': 'Balanced cardio and core training to burn fat, build endurance, and maintain general physical fitness.',
                'frequency': '5 days a week',
                'duration': '45-60 minutes',
                'exercises': [
                    {'name': 'Brisk Walking or Jogging', 'sets': '1 session', 'reps': '25-30 mins', 'benefit': 'Burns calories and builds stamina.'},
                    {'name': 'Bodyweight Squats', 'sets': '3 sets', 'reps': '12-15 reps', 'benefit': 'Strengthens glutes and thighs.'},
                    {'name': 'Plank Hold', 'sets': '3 sets', 'reps': '30-45 seconds', 'benefit': 'Strengthens the abdominal core.'},
                    {'name': 'Jumping Jacks', 'sets': '3 sets', 'reps': '20 reps', 'benefit': 'High-energy full body cardio.'},
                    {'name': 'Crunches', 'sets': '3 sets', 'reps': '15 reps', 'benefit': 'Tones upper abdominals.'}
                ],
                'precaution': 'Wear proper running shoes and stay hydrated during the session.'
            },
            2: { # High Intensity Gym / Strength
                'title': 'Hypertrophy & Strength Training Routine',
                'description': 'Structured resistance exercises targeting muscle groups to increase lean muscle mass and skeletal strength.',
                'frequency': '4-5 days a week (Split routine)',
                'duration': '60 minutes',
                'exercises': [
                    {'name': 'Barbell Squats', 'sets': '4 sets', 'reps': '8-12 reps', 'benefit': 'Builds powerful lower body strength.'},
                    {'name': 'Dumbbell Bench Press', 'sets': '3 sets', 'reps': '10-12 reps', 'benefit': 'Develops chest and tricep muscles.'},
                    {'name': 'Lat Pulldowns / Pull-ups', 'sets': '3 sets', 'reps': '8-12 reps', 'benefit': 'Strengthens back and biceps.'},
                    {'name': 'Overhead Shoulder Press', 'sets': '3 sets', 'reps': '10 reps', 'benefit': 'Improves shoulder stability and power.'},
                    {'name': 'Dumbbell Bicep Curls / Tricep Pushdowns', 'sets': '3 sets', 'reps': '12 reps', 'benefit': 'Builds arm muscle definition.'}
                ],
                'precaution': 'Focus on proper form before increasing weight. Warm up for 10 minutes prior.'
            }
        }
        
        # 3. WATER INTAKE LOGIC
        # Standard: 35ml per kg of bodyweight, adjusted for activity level
        water_base = weight * 0.035 # Liters
        activity_addition = {
            'Sedentary': 0.0,
            'Lightly Active': 0.3,
            'Moderately Active': 0.6,
            'Very Active': 1.0
        }
        water_target = round(water_base + activity_addition.get(activity_level, 0.5), 1)
        
        # 4. SLEEP SUGGESTION LOGIC
        if age > 60:
            sleep_hours = "7 - 8 Hours"
            sleep_note = "Older adults may experience changes in sleep patterns, but still require a full night of rest. Maintain a strict circadian rhythm."
        elif age < 25:
            sleep_hours = "8 - 9 Hours"
            sleep_note = "Younger adults are still undergoing physical and cognitive development. Prioritize consistent sleep schedules."
        else:
            sleep_hours = "7 - 9 Hours"
            sleep_note = "Ideal sleep duration to enable muscle recovery, cognitive function, and hormonal balance."
            
        # 5. GENERAL WELLNESS TIPS
        all_tips = [
            "Chew your food 32 times. Mindful, slow eating aids digestion and prevents overeating.",
            "Avoid screens at least 45 minutes before bed. Blue light disrupts melatonin production.",
            "Take a short walk after meals, particularly dinner, to help control blood sugar spikes.",
            "Practice the 20-20-20 rule for eye health: every 20 minutes look at something 20 feet away for 20 seconds.",
            "Start your morning with a glass of warm lemon water to balance internal pH and kickstart digestion.",
            "Replace desk sitting with active standing blocks of 10 minutes every hour.",
            "Manage stress via box breathing: breathe in for 4s, hold for 4s, exhale for 4s, hold for 4s.",
            "Eat home-cooked food. Eating out regularly increases hidden calorie intake through oil and sugar.",
            "Include raw fiber in your lunch like carrots, radish, and cucumbers.",
            "Stay consistent with sleep schedules. Waking up at the same time daily stabilizes your body clock."
        ]
        
        selected_tips = random.sample(all_tips, 3)
        
        # Formulate response
        return {
            'bmi': bmi,
            'bmi_category': bmi_category,
            'diet_plan': diet_plans[diet_cat],
            'exercise_plan': exercise_plans[exercise_cat],
            'water_target_liters': water_target,
            'water_glasses': int(round(water_target * 4)), # ~250ml per glass
            'sleep_target_hours': sleep_hours,
            'sleep_note': sleep_note,
            'wellness_tips': selected_tips,
            'engine_source': engine_source
        }

# Instantiate global AI recommendation engine
ai_engine = AIRecommendationEngine()
