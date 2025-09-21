class SongHistory:
    def __init__(self, max_size = 50):
        self.history = []
        self.current_index = -1
        self.max_size = max_size

    def add_song(self, song):
        if len(self.history) >= self.max_size:
            self.history.pop(0)
        self.history.append(song)
        self.current_index = len(self.history) - 1

    def get_previous_song(self):
        """Get the previous song without circular navigation."""
        if not self.history or self.current_index <= 0:
            return None

        self.current_index -= 1
        return self.history[self.current_index]

    def get_next_song(self):
        """Get the next song without circular navigation."""
        if not self.history or self.current_index >= len(self.history) - 1:
            return None

        self.current_index += 1
        return self.history[self.current_index]

    def get_current_song(self):
        if 0 <= self.current_index < len(self.history):
            return self.history[self.current_index]
        return None

    def clear_history(self):
        self.history = []
        self.current_index = -1
    def remove_song(self, index):
        """Remove a song at a specific index."""
        if 0 <= index < len(self.history):
            del self.history[index]
            # Adjust the current index if necessary
            if self.current_index >= len(self.history):
                self.current_index = len(self.history) - 1

    def get_full_history(self):
        """Return the full history as a list."""
        return self.history[:]

    def is_empty(self):
        return len(self.history) == 0