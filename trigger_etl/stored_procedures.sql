DROP PROCEDURE IF EXISTS search_legislation
DROP PROCEDURE IF EXISTS search_any

GO

CREATE PROCEDURE search_legislation 
	@Jurisdiction nvarchar(30)=null, 
	@IssuingBody nvarchar(30)=null,
	@Title nvarchar(30)=null,
	@Content nvarchar(255)=null
AS
    select 
        p.id as PartID, 
        title as LegislationTitle,
        j.name as JurisdictionName,
        i.name as IssuingBodyName,
        content_html_stipped as PartContent
    from [dbo].[part] p    
        join [dbo].[legislation] l on l.id = p.legislation_id
        join [dbo].[jurisdiction] j on l.jurisdiction_id = j.id
        join [dbo].[issuing_body] i on l.issuing_body_id = i.id
    where 
		((@Jurisdiction is null) or (j.name = @Jurisdiction)) and 
		((@IssuingBody is null) or (i.name = @IssuingBody)) and 
		((@Title is null) or (title like '%' + @Title + '%')) and
		((@Content is null) or (content like '%' + @Content + '%'))

GO

CREATE PROCEDURE search_any @Search nvarchar(30)
AS
BEGIN
    select 
        p.id as PartID, 
        title as LegislationTitle,
        j.name as JurisdictionName,
        i.name as IssuingBodyName,
        content_html_stipped as PartContent
    from [dbo].[part] p
        join [dbo].[legislation] l on l.id = p.legislation_id
        join [dbo].[jurisdiction] j on l.jurisdiction_id = j.id
        join [dbo].[issuing_body] i on l.issuing_body_id = i.id
    where  
		title like '%' + @Search + '%' or
        j.name like '%' + @Search + '%' or
        i.name like '%' + @Search + '%' or
		content like '%' + @Search + '%'
END
