def update_xp(user, amount):
    if not hasattr(user, 'xp'):
        user.xp = 0
    if not hasattr(user, 'level'):
        user.level = 1

    user.xp += amount

    next_level = user.level * 100
    if user.xp >= next_level:
        user.level += 1
        user.xp = user.xp - next_level

    user.save()
