# AIAP Technical Assessment — Decision Log

**Candidate name (as in NRIC):**  Alex Teo*

**Email (as used in your application):** alexteo97@hotmail.com

---

## A note on this document

This decision log is the primary instrument by which we understand your thinking. The questions below cover the reasoning behind your work — from how you define the problem at the start to the decisions you made during the work itself. Do answer all five questions in your own words. 

You may use AI assistance freely on the technical deliverables (the EDA and the ML pipeline), but this Decision Log itself should be written by you — it is the record of your own thinking that we cross-check against your chat history.


---

## 1. Clarifying questions

What questions would you ask to better define and narrow the problem statement? For each question, briefly explain how the answer would meaningfully change your approach. 

Note: If it helps your decision-making, you may assume and list out the stakeholders' likely answers.


**Your answer:

Q1. What would be the call-to-action we will formulate at the end. As we already know, the pain point of the issue is the potential loss of revenue and risk of rooms being reserved for guests who may eventually cancel or not show up. However, the main question is what the stakeholder actually wants to do once we are able to identify high-risk reservations. This is because an alert system alone may only achieve limited help for stakeholders but might be limited as compared to an actual call-to-action afterwards. The hotel may want staff to reach out to high-risk guests, prioritise those bookings for review, support inventory planning, or test separate interventions such as incentives. These different actions would affect how I frame the problem and how the AI model should eventually be used.

Q2. How would the presence of AI made a difference if no AI intervention was used at all in this project - and how will it impact current way of working. I want to understand what is the level of AI does the hotel currently adopts in their workflow, what do they do without AI. All these will really help the smoothen the adoption curve for them once we develop our AI model. Are staff right now mainly relying on intuition  or actually looking through the data at least / review bookings - to make decisions or assumptions. Once AI is introduced, what should it do to help stakehodlers do their job better (e.g. maybe prioritising which bookings to review due to high risk, or maybe even help reduce overall amount of times to check things manually - like their booking for examplke). This ensures ML solution is solving a real problem rather than just using AI for sake of using AI.

Q3. What does "better pricing" means? Does the stakeholder mean pricing that would lead to overall higher revenues, more profits, and also during what period, just the peak season? or all year round (if this is really the better pricing). Better pricing could also just mean better competitive rates than their competitors so clearer crisper definition of 'better pricing' would really help steer direction of project clearer.**



---

## 2. Defining the Problem Statement

Restate, in your own words, the refined problem you decided to solve. List your key assumptions. Briefly note what other framings you considered, and what you deliberately left out or scoped down, and why.


**Your answer:

The refined problem i decided to solve is to actually predict if hotel reservations made are at higher risk of cancellation / no-shows instead of the desired outcome of a complete stay. I would say I am not aiming to automatically cancel / overbook hotel rooms first in antiicpation of high-risk reservations; I am instead aiming to give the stakeholders earlier visibility of such high-risk reservations so they can give attention to such reservations and come up with better call-to-actions, and even within the group of high-risk reservations which might even need more attention.

One key assumption I made is that ML prediction only takes palce after a reservation is made but before final outcome is known (whether leads to no-show / cancellation / complete stay). With this in mind, I would only use information available at that point, and not consider fields such as final reservation status, actual assigned room type and post-stay information. I considered few other ways to frame the problem statement too, like one where we focus only on last minute cancellations, but during EDA we see that medican cancellation was only happening more than 50 days before actual room check-in date (this clearly shows real issue was much more than just last-minute cancellations as stated by stakeholders). I at one point also looked into the idea of price optimisation as raised by stakeholders. However during EDA my findings on the data clearly shows only historical ADR mainly and does not tell us what optimal pricing should have been. WIthout optimal pricing evidence, when we build our ML model only fed by historical ADR, pricing can never truly be optimised. We might as an example know historically a certain price e.g. $200 shows highest revenue / profit due to least amount of no show / cancellation within this price but this does not factor alot of other essential factors: price elasticity / demand, competitor / market pricing variables etc. And also what if maybe $230 was the optimal pricing but because we never ever use such price we can never rely on our ML model to determine that this is actually a better pricing for higher revenue or profit outcome. With this crux in mind, I decide to focus less on pricing model ML and proceed with reservation fall-through prediction as the more justifiable ML model for our case.**





---

## 3. Key decisions during Solution Development

Walk through three key decisions you made during Solution Development. For each: what options did you consider, what did you choose, and why? These can be technical (modelling choices, feature handling, evaluation metrics) or about the work itself (what to prioritise, what to drop, how to spend your time).


**Your answer:

Key Decision 1: How i decide to split the data used for trainin / testing data. I used a chronological split instead of the common approach of randomly splitting the data - this is because in our case of hotel bookings, it makes sense that hotel use historical reservations to identify patterns and trends, and then apply the model for future reservations. So thats why I used earlier period for training, mid-period for validation, and kept the latest period as the final untouched test set. This also help me see how the ML model fare when booking behavior changes over time.

Key Decision 2: At one point I made a exclusion of few fields to not use in my ML model, as sometimes less is more where we shouldnt simply use every column that might appear useful at first. Fields like 'reservation_status, reservation_status_date, assigned_room_type, booking_changes' or even identifiers like email / booking ID. Some of these fields are only known or available close to the final outcome date or even after, as such including them in our model would not be the most realistic because it we are effectively giving future information. I therefore set the prediction point / timeframe first and only used fields / predictors that should be reasonably available before final outcome (since the key is to build a ML model that is realistically workable for the stakeholders, and not a 'beautiful' theoretical ML model). I excluded identifiers as I dont think including them will help with generalisable booking behavior.

Key Decision 3: I go with my vision of "less is more" when deciding and even ultimately selecting which models i would use in my ML model - therefore keeping my model comparison simple instead of trying many different ML algorithms. First i used a Dummy model as the basic benchmark to show what performance looks like when model is not really learning useful patterns. Next i used Logistic Regression as a simpler proper ML model, and also Random Forest as a more flexible model that can work with more complex combinations of booking information. The Dummy model with average precision of 0.365 shows what a "no real learning" baseline would looke like. While our Logistic Regression achieved around 0.804, showing that the booking information does contain some useful predictive pattern. Our Rnadom Forest performed slightly better with 0.841 Average Precision and also a higher ROC-AUC then Logical Regression (0.887 > 0.857). This therefore indicates that at least for our case, it is better to use a more flexible model that provides slightly more value. I then did a small amount of performance finetuning rather than introducing much more unecesary models out of our scope since I did not think that trying many more models would add enough value to justify the extra layers of complexity.**


---

## 4. Use of the AI assistant

Where did you use the AI assistant in this work? Give three specific examples of something the assistant suggested that you changed, rejected, or significantly modified — and explain your reasoning.


**Your answer:

Example 1: My AI assistant initially suggested that I could tune the Random Forest using quite a number of different settings. I decided not to go with this and only tested a few settings instead. The main reason was because the original Random Forest was already doing quite well, and after tuning, the Average Precision only improved from around 0.8413 to 0.8434. Since the improvement was quite small, I felt there was not much value spending a lot more time trying many different settings just to improve the result slightly. I therefore chose to keep the model simpler instead of making the process more complicated.

Example 2: The AI assistant suggested one possible way of choosing the alert level, which was to try and catch as many fall-through bookings as possible while still keeping a certain level of correct alerts, for example 70%. I decided not to use the 70% because this number was never actually given by the stakeholder in our case. We also do not know exactly how costly it would be to wrongly flag a booking that eventually completes, compared to missing a booking that actually cancels or no-shows (which could potentially have a bigger business impact). I did not want to make up a business requirement that was never even given in the first place, thefore in the end I used F2 because it gives more importance to catching more of the actual fall-through cases, which fits better with my idea of using the model as an early warning / screening tool rather than automatically taking action on the booking.

Example 3: The AI assistant also pointed out that I should not assume that Random Forest score of for example 0.8 automatically means there is exactly 80% real-life chance that booking will fall through. It suggested that I could do further checking and even add another step to adjust these scores if really necessary. I did check the Brier score as one of my evaluation results, but I decide not to add another extra layer to the model because I did not see enough reason to make the solution more complicated at this stage. Instead, I rather change / rephrase how I would describe the result and call it a “risk score” rather than saying it is an exact probability.**





---

## 5. Next Steps

If you had one more week to continue this project, what would you do next, and why? What signals from your current work make those the right next steps?


**Your answer:

If I had an additional week I can propose maybe a small trial to actually test effectiveness of intervention / call-to-action methods. Like once we run our ML model and gather a list of high-risk bookings, maybe some will receive intervention methods and some just receive BAU treatment. We then compare the outcomes and see whether or not our intervention is helpful. Intervention can be like (simple reminder, contacting the guest, or confirmation request once more, or even any incentive we think might improve our cancellation / no-show rates).

Lastly, throughout the entire week, I would set up a way that allows whoever takes over the model to continue checking the model using newer booking data to see if its performance drops over time. If customer behaviour, hotel pricing or booking channels change, the old patterns learned by the model may become not as useful and the model may eventually need to be retrained for better results in the future.**





---
