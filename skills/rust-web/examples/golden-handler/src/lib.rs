#[derive(Debug, Eq, PartialEq)]
pub struct Response {
    pub status: u16,
    pub error_code: Option<&'static str>,
    pub body: String,
}

#[derive(Debug, Eq, PartialEq)]
pub enum GetUserError {
    InvalidId,
    NotFound,
    Unavailable,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct LookupError;

pub trait UserLookup {
    fn name_by_id(&self, id: u64) -> Result<Option<String>, LookupError>;
}

pub fn get_user(path_id: &str, users: &impl UserLookup) -> Response {
    let result = path_id
        .parse::<u64>()
        .map_err(|_| GetUserError::InvalidId)
        .and_then(|id| {
            users
                .name_by_id(id)
                .map_err(|_| GetUserError::Unavailable)?
                .ok_or(GetUserError::NotFound)
        });

    match result {
        Ok(name) => Response {
            status: 200,
            error_code: None,
            body: format!("user={name}"),
        },
        Err(GetUserError::InvalidId) => error(400, "invalid_id", "id must be an integer"),
        Err(GetUserError::NotFound) => error(404, "user_not_found", "user was not found"),
        Err(GetUserError::Unavailable) => {
            error(503, "dependency_unavailable", "service is unavailable")
        }
    }
}

fn error(status: u16, error_code: &'static str, message: &'static str) -> Response {
    Response {
        status,
        error_code: Some(error_code),
        body: message.to_owned(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    struct FakeUsers {
        result: Result<Option<String>, LookupError>,
    }

    impl UserLookup for FakeUsers {
        fn name_by_id(&self, _id: u64) -> Result<Option<String>, LookupError> {
            self.result.clone()
        }
    }

    #[test]
    fn keeps_transport_validation_at_the_boundary() {
        let users = FakeUsers { result: Ok(None) };

        let response = get_user("not-an-id", &users);

        assert_eq!(response.status, 400);
        assert_eq!(response.error_code, Some("invalid_id"));
    }

    #[test]
    fn maps_not_found_without_leaking_adapter_details() {
        let users = FakeUsers { result: Ok(None) };

        let response = get_user("42", &users);

        assert_eq!(response.status, 404);
        assert_eq!(response.error_code, Some("user_not_found"));
    }

    #[test]
    fn maps_adapter_failure_to_a_stable_response() {
        let users = FakeUsers {
            result: Err(LookupError),
        };

        let response = get_user("42", &users);

        assert_eq!(response.status, 503);
        assert_eq!(response.error_code, Some("dependency_unavailable"));
        assert!(!response.body.contains("database"));
    }
}
