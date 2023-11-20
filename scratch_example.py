from dependencies import scratch_project, scratch_enums
# import scratch_compiler

sprite = scratch_project.Sprite("Sprite1")

def type_writer(message: str, wait_for: int):
    for i in message:
        sprite.say(i)
        sprite.wait(wait_for)


def count_up(up_to: int, delay: int):
    for i in range(up_to):
        sprite.say(i)
        sprite.wait(delay)

sprite.say("Hello world!")
sprite.wait(1)
sprite.say("I've waited 1 second!")
sprite.wait(2)
sprite.say("Now I'm going to say the entire alphabet!")
sprite.wait(1)
type_writer("abcdefghijklmnopqrstuvwxyz", 0.5)
sprite.say("Now I'm going to count to 10!")
sprite.wait(1)
count_up(10, 0.5)