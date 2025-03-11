import asyncio

class Logger:
    def __init__(self, message_queue, playlist_size):
        self.message_queue = message_queue
        self.playlist_size = playlist_size
        self.counter = 1
    
    def debug(self, msg):
        if "Downloading item" in msg:
            print(msg)
            self.message_queue.put_nowait(f"*Downloading song {self.counter} of {self.playlist_size}*")
            self.counter += 1

            # All songs are downloaded
            if (self.counter > self.playlist_size):
                self.message_queue.put_nowait("DONE")
    
    def warning(self, msg):
        print(msg)
    
    def error(self, msg):
        print(msg)

async def start_message_sender(message_queue, ctx):
    """Creates and returns a task that monitors the queue and sends messages"""
    async def message_sender():
        initial_message = await ctx.send("**Downloading songs from playlist...** Please wait")
        progress_message = await ctx.send("*Starting download...*")

        while True:
            msg = await message_queue.get()

            # Delete all messages
            if msg == "DONE":
                await progress_message.delete()
                await initial_message.delete()
                message_queue.task_done()
            # Edit progress message
            else:
                await progress_message.edit(content=msg)
                message_queue.task_done()
    
    return asyncio.create_task(message_sender())