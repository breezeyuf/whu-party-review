"""Expiry review only. Never deletes, moves, or modifies original material files."""
from dateutil.relativedelta import relativedelta
from sqlalchemy import String, cast
from errors import forbidden, not_found, unprocessable
from models import Material, MaterialVersion, AuditLog
from services.audit import log
from utils import get_setting, now


def _eligible(db,actor):
    if actor.role not in ('SYS_ADMIN','ORG_ADMIN'): raise forbidden()
    years=int(get_setting(db,'retention',{}).get('material_years') or 10)
    cutoff=now()-relativedelta(years=years)
    return db.query(MaterialVersion).filter(MaterialVersion.uploaded_at<=cutoff),years


def list_expired(db,actor,page=1,page_size=20,status='pending'):
    query,years=_eligible(db,actor)
    confirmed=db.query(AuditLog.id).filter(AuditLog.action=='RETENTION_KEEP',AuditLog.object_type=='material_version',
                AuditLog.object_id==cast(MaterialVersion.id,String)).exists()
    query=query.filter(confirmed if status=='confirmed' else ~confirmed)
    total=query.count()
    rows=query.order_by(MaterialVersion.uploaded_at,MaterialVersion.id).offset((page-1)*page_size).limit(page_size).all()
    items=[]
    for row in rows:
        material=db.get(Material,row.material_id)
        items.append({'id':row.id,'material_id':row.material_id,'title':material.title if material else '',
                      'filename':row.original_filename,'version_no':row.version_no,'uploaded_at':row.uploaded_at.isoformat(),
                      'due_at':(row.uploaded_at+relativedelta(years=years)).isoformat(),'status':status})
    return {'items':items,'total':total,'page':page,'page_size':page_size,'material_years':years,
            'policy':'按版本上传日期计算；管理员确认后继续保留原件，不删除文件'}


def confirm_keep(db,actor,version_id,reason):
    if not isinstance(reason,str) or not reason.strip() or len(reason)>500:
        raise unprocessable('请填写 1 至 500 字保留原因')
    query,years=_eligible(db,actor)
    row=query.filter(MaterialVersion.id==version_id).with_for_update().first()
    if not row: raise not_found('未找到已到期材料版本')
    existing=db.query(AuditLog.id).filter(AuditLog.action=='RETENTION_KEEP',AuditLog.object_type=='material_version',
                                        AuditLog.object_id==str(version_id)).first()
    if not existing:
        log(db,actor,'RETENTION_KEEP','material_version',version_id,{'reason':reason.strip(),'material_years':years,'original_preserved':True})
        db.flush()
    return {'ok':True,'original_preserved':True}
