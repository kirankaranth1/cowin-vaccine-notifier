## cowin-vaccine-notifier

This app checks for vaccine availbility in the PIN codes near you every 30 minutes and sends email notifications if there are any updates. 
To register for these notifications [fill this form with your details.](https://forms.gle/xYFcdM193dPtneGSA) https://forms.gle/xYFcdM193dPtneGSA
## Sample email:
![Sample email](/img/emailsample.png)

# Todos:
- ~~Build a front end to accept input~~ Currently usig Google forms as input
- Implement async everywhere, current code won't scale
- ~~Build system to remember current status to send further emails only if there is a change~~ Done.
- ~~Deploy to remote server and design scheduling~~ Current using Windows Task scheduler on a VM
