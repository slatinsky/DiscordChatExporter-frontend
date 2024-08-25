class Formatters:
    @staticmethod
    def human_file_size(file_size_bytes: int) -> str:
        """
        returns file size in human readable format
        """
        # round to 2 decimal places
        if file_size_bytes < 1024:
            return f'{file_size_bytes} B'
        elif file_size_bytes < 1024 * 1024:
            return f'{round(file_size_bytes / 1024, 2)} KB'
        elif file_size_bytes < 1024 * 1024 * 1024:
            return f'{round(file_size_bytes / 1024 / 1024, 2)} MB'
        else:
            return f'{round(file_size_bytes / 1024 / 1024 / 1024, 2)} GB'

    @staticmethod
    def human_time(seconds_total: int) -> str:
        """
        returns time in format HH:MM:SS
        """
        hours, remainder = divmod(seconds_total, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    @staticmethod
    def pad_id(id: int) -> str:
        if id == None:
            return None
        return str(id).zfill(24)