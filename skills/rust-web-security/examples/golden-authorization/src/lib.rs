#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Role {
    Member,
    TenantAdmin,
}

#[derive(Debug, Eq, PartialEq)]
pub struct Principal {
    pub subject_id: u64,
    pub tenant_id: u64,
    pub role: Role,
}

#[derive(Debug, Eq, PartialEq)]
pub struct Document {
    pub owner_id: u64,
    pub tenant_id: u64,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Action {
    Read,
    Update,
    Delete,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Decision {
    Allow,
    Deny,
}

pub fn authorize(principal: &Principal, action: Action, document: &Document) -> Decision {
    if principal.tenant_id != document.tenant_id {
        return Decision::Deny;
    }

    match (principal.role, action) {
        (Role::TenantAdmin, Action::Read | Action::Update) => Decision::Allow,
        (Role::Member, Action::Read | Action::Update)
            if principal.subject_id == document.owner_id =>
        {
            Decision::Allow
        }
        _ => Decision::Deny,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn document() -> Document {
        Document {
            owner_id: 7,
            tenant_id: 10,
        }
    }

    #[test]
    fn allows_an_owner_to_update_their_document() {
        let owner = Principal {
            subject_id: 7,
            tenant_id: 10,
            role: Role::Member,
        };

        assert_eq!(
            authorize(&owner, Action::Update, &document()),
            Decision::Allow
        );
    }

    #[test]
    fn denies_cross_tenant_access_even_for_a_tenant_admin() {
        let other_tenant_admin = Principal {
            subject_id: 9,
            tenant_id: 11,
            role: Role::TenantAdmin,
        };

        assert_eq!(
            authorize(&other_tenant_admin, Action::Read, &document()),
            Decision::Deny
        );
    }

    #[test]
    fn denies_actions_without_an_explicit_grant() {
        let tenant_admin = Principal {
            subject_id: 9,
            tenant_id: 10,
            role: Role::TenantAdmin,
        };

        assert_eq!(
            authorize(&tenant_admin, Action::Delete, &document()),
            Decision::Deny
        );
    }
}
