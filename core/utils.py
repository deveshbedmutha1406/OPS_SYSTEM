from crontab import CronTab


def remove_cron_job(command):
    # Access the user's crontab
    cron = CronTab(user=True)

    # Find and remove the specific cron job
    for job in cron:
        if job.command in command:
            cron.remove(job)

    # Write the changes to the crontab
    cron.write()


def add_cron_job(cron_expression, script_path):
    cron = CronTab(user=True)
    job = cron.new(command=script_path)
    job.setall(cron_expression)
    cron.write()
