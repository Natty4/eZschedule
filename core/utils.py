from datetime import datetime, timedelta

def generate_available_slots(business_hours, reserved_slots, task_duration, workers, reference_date=None):
    available_slots = {}
    current_datetime = datetime.now()
    
    for day_offset in range(7):  # loop for the next 7 days
        check_date = current_datetime + timedelta(days=day_offset)
        day_name = check_date.strftime("%A").lower()
        
        for worker_id in workers:
            worker_business_hours = business_hours.get(str(worker_id), [])
            worker_reserved_slots = reserved_slots.get(str(worker_id), [])
            
            # worker_slots is now a list of dictionaries containing 'day', 'date', and 'slots'
            worker_slots = available_slots.setdefault(worker_id, [])
            
            # find business hour for this specific day
            business_day_hours = next((bh for bh in worker_business_hours if bh['day'].lower() == day_name), None)
            if not business_day_hours or business_day_hours['is_closed']:
                continue  # skip if no business hours or closed that day
            
            open_time = business_day_hours['open_time']
            close_time = business_day_hours['close_time']
            
            # convert open/close time strings to datetime object
            open_time_dt = datetime.strptime(open_time, "%H:%M").replace(
                year=check_date.year, month=check_date.month, day=check_date.day
            )
            
            close_time_dt = datetime.strptime(close_time, "%H:%M").replace(
                year=check_date.year, month=check_date.month, day=check_date.day
            )
    
            # if today, ensure only future slots are considered 
            if day_offset == 0:
                current_time_dt = current_datetime.replace(second=0, microsecond=0)
                if current_time_dt >= close_time_dt:
                    continue  # skip if past closing time 
                
                # check if there is a reserved slot that just ended before now 
                next_possible_time = open_time_dt  # default to open time 
                while next_possible_time + task_duration <= current_time_dt:
                    next_possible_time += task_duration
                    
                open_time_dt = next_possible_time  # set the new start time
            
            # generate available slots
            daily_slots = []
            current_time_slot = open_time_dt
            
            while (current_time_slot + task_duration) <= close_time_dt:
                next_time_slot = current_time_slot + task_duration
                
                # check if this slot overlaps with any reserved slot     
                conflict = any(
                    res_start_dt < next_time_slot and res_end_dt > current_time_slot
                    for res_start, res_end in worker_reserved_slots
                    for res_start_dt, res_end_dt in [(
                        datetime.strptime(res_start, "%Y-%m-%d-%H:%M"),
                        datetime.strptime(res_end, "%Y-%m-%d-%H:%M")
                    )]
                )
                
                if not conflict:
                    daily_slots.append({
                        "start_time": current_time_slot.strftime("%Y-%m-%d-%H:%M"),
                        "end_time": next_time_slot.strftime("%Y-%m-%d-%H:%M")
                    })
                    
                current_time_slot = next_time_slot  # move to next slot
            
            # Add day and date to the slots
            if daily_slots:  # Only add the day if there are slots available
                worker_slots.append({
                    'day': day_name,
                    'date': check_date.strftime('%Y-%m-%d'),
                    'slots': daily_slots
                })
    
    return available_slots
