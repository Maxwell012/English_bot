from pydantic import BaseModel
from datetime import datetime


class Base(BaseModel):
    def __str__(self):
        def format_item(key, item, indent=0):
            key_formatted = f"{' ' * indent}🔹 " \
                            f"<b>{key.capitalize()}</b>"
            if isinstance(item, datetime):
                return f"{key_formatted}: {item.strftime('%d/%m/%Y, %H:%M:%S')}"
            elif isinstance(item, dict):
                dict_content = "\n".join(
                    format_item(k, v, indent + 4) for k, v in item.items()
                )
                return f"{key_formatted}:\n{dict_content}"
            else:
                return f"{key_formatted}: {item}"

        text = "\n".join(
            format_item(key, item) for key, item in self.model_dump().items()
        )
        return text


class SchemaIn(Base):
    pass


class SchemaOut(Base):
    pass


class SchemaToDB(Base):
    pass


class SchemaFromDB(Base):
    pass


class SchemaUpdate(Base):
    pass
