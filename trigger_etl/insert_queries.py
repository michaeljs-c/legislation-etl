LEGISLATION_QUERY = """
    merge into 
        [dbo].[legislation] with (holdlock) t  
    using 
        (values (?, ?, ?, ?, ?)) s([id], [title], [native_title], [jurisdiction_id], [issuing_body_id])
    on 
        t.[id] = s.[id]
    when not matched then 
        insert values (s.[id], s.[title], s.[native_title], s.[jurisdiction_id], s.[issuing_body_id]);
"""

JURISDICTION_QUERY = """
    merge into 
        [dbo].[jurisdiction] with (holdlock) t  
    using 
        (values (?, ?)) s([id], [name])
    on 
        t.[id] = s.[id]
    when not matched then 
        insert values (s.[id], s.[name]);
"""

ISSUING_BODY_QUERY = """
    merge into 
        [dbo].[issuing_body] with (holdlock) t  
    using 
        (values (?, ?)) s([id], [name])
    on 
        t.[id] = s.[id]
    when not matched then 
        insert values (s.[id], s.[name]);
"""

PART_QUERY = """
    merge into 
        [dbo].[part] with (holdlock) t  
    using 
        (values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) s([id], [version_id], [version_ordinal], [legislation_id], [legislation_version_ordinal], [parent_id], [parent_version_id], [parent_version_ordinal], [order_num], [content], [content_html_stripped], [native_content], [native_content_html_stripped])
    on 
        t.[id] = s.[id] and t.[version_ordinal] = s.[version_ordinal]
    when not matched then 
        insert values (s.[id], s.[version_id], s.[version_ordinal], s.[legislation_id], s.[legislation_version_ordinal], s.[parent_id], s.[parent_version_id], s.[parent_version_ordinal], s.[order_num], s.[content], [content_html_stripped], s.[native_content], s.[native_content_html_stripped]);
"""

LEGISLATION_VERSION_QUERY = "INSERT INTO legislation_version (legislation_id, version_ordinal, version_id) VALUES (?, ?, ?)"
