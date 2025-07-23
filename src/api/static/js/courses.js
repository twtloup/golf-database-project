// Courses Page JavaScript

class CoursesManager {
    constructor() {
        this.isLoading = false;
        
        this.initializeElements();
        this.loadCourses();
    }
    
    initializeElements() {
        this.coursesGrid = document.getElementById('coursesGrid');
    }
    
    async loadCourses() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading();
        
        try {
            const response = await fetch('/api/courses');
            const data = await response.json();
            
            if (response.ok) {
                this.displayCourses(data.courses);
            } else {
                this.showError(data.error || 'Failed to load courses');
            }
        } catch (error) {
            console.error('Error loading courses:', error);
            this.showError('Network error occurred');
        } finally {
            this.isLoading = false;
        }
    }
    
    displayCourses(courses) {
        if (!courses || courses.length === 0) {
            this.coursesGrid.innerHTML = `
                <div class="no-results">
                    <h3>No courses found</h3>
                    <p>Course data is currently unavailable</p>
                </div>
            `;
            return;
        }
        
        const coursesHTML = courses.map(course => this.createCourseCard(course)).join('');
        this.coursesGrid.innerHTML = coursesHTML;
        
        // Add click handlers for course cards
        this.coursesGrid.querySelectorAll('.course-card').forEach(card => {
            card.addEventListener('click', () => {
                const courseId = card.dataset.courseId;
                this.showCourseDetails(courseId, card);
            });
        });
    }
    
    createCourseCard(course) {
        const location = course.location || 'Location unknown';
        const par = course.total_par || 'Par unknown';
        const tournamentCount = course.tournament_count || 0;
        
        return `
            <div class="course-card" data-course-id="${course.course_id}">
                <div class="course-name">${course.course_name}</div>
                <div class="course-location">${location}</div>
                
                <div class="course-stats">
                    <div class="course-stat">
                        <div class="label">Par</div>
                        <div class="value">${par}</div>
                    </div>
                    <div class="course-stat">
                        <div class="label">Tournaments</div>
                        <div class="value">${tournamentCount}</div>
                    </div>
                </div>
                
                <div class="course-actions">
                    <button class="btn btn-primary btn-small">View Details</button>
                </div>
            </div>
        `;
    }
    
    async showCourseDetails(courseId, cardElement) {
        const courseName = cardElement.querySelector('.course-name').textContent;
        const courseLocation = cardElement.querySelector('.course-location').textContent;
        
        try {
            // Fetch tournaments at this course
            const response = await fetch(`/api/tournaments?search=${encodeURIComponent(courseName)}`);
            const data = await response.json();
            
            if (response.ok) {
                this.displayCourseModal(courseName, courseLocation, data.tournaments || []);
            } else {
                this.showErrorModal('Failed to load course details');
            }
        } catch (error) {
            console.error('Error loading course details:', error);
            this.showErrorModal('Network error occurred');
        }
    }
    
    displayCourseModal(courseName, location, tournaments) {
        const modalHTML = `
            <div class="modal-overlay" onclick="this.remove()">
                <div class="modal-content" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <div>
                            <h2>${courseName}</h2>
                            <p class="course-location-modal">${location}</p>
                        </div>
                        <button class="close-btn" onclick="this.closest('.modal-overlay').remove()">×</button>
                    </div>
                    <div class="modal-body">
                        ${this.createCourseDetailsContent(tournaments)}
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }
    
    createCourseDetailsContent(tournaments) {
        if (!tournaments || tournaments.length === 0) {
            return `
                <div class="no-results">
                    <h3>No tournament data available</h3>
                    <p>Tournament history for this course is currently unavailable.</p>
                </div>
            `;
        }
        
        // Sort tournaments by date (most recent first)
        const sortedTournaments = tournaments.sort((a, b) => {
            if (a.tournament_date && b.tournament_date) {
                return new Date(b.tournament_date) - new Date(a.tournament_date);
            }
            return 0;
        });
        
        return `
            <div class="course-details">
                <h3>Tournament History (${tournaments.length} events)</h3>
                <div class="tournaments-list-modal">
                    ${sortedTournaments.map(tournament => this.createTournamentListItem(tournament)).join('')}
                </div>
            </div>
        `;
    }
    
    createTournamentListItem(tournament) {
        const date = tournament.tournament_date ? new Date(tournament.tournament_date).getFullYear() : 'TBD';
        const purse = tournament.purse_millions ? `$${tournament.purse_millions}M` : '';
        const players = tournament.player_count ? `${tournament.player_count} players` : '';
        
        return `
            <div class="tournament-list-item">
                <div class="tournament-info">
                    <div class="tournament-name-small">${tournament.tournament_name}</div>
                    <div class="tournament-meta">
                        ${date} • ${purse} • ${players}
                    </div>
                </div>
            </div>
        `;
    }
    
    showErrorModal(message) {
        const modalHTML = `
            <div class="modal-overlay" onclick="this.remove()">
                <div class="modal-content" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h2>Error</h2>
                        <button class="close-btn" onclick="this.closest('.modal-overlay').remove()">×</button>
                    </div>
                    <div class="modal-body">
                        <div class="error">
                            <p>${message}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }
    
    showLoading() {
        this.coursesGrid.innerHTML = '<div class="loading">Loading courses...</div>';
    }
    
    showError(message) {
        this.coursesGrid.innerHTML = `
            <div class="error">
                <h3>Error</h3>
                <p>${message}</p>
                <button onclick="coursesManager.loadCourses()" class="btn btn-primary">Try Again</button>
            </div>
        `;
    }
}

// Course-specific styles
const courseModalStyles = `
<style>
.course-actions {
    margin-top: 1rem;
    text-align: center;
}

.btn-small {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
}

.course-stat {
    text-align: center;
}

.course-stat .label {
    font-size: 0.8rem;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.course-stat .value {
    font-size: 1.2rem;
    font-weight: 600;
    color: #2c5530;
    margin-top: 0.25rem;
}

.course-location-modal {
    color: #666;
    font-size: 1rem;
    margin: 0.5rem 0 0 0;
}

.tournaments-list-modal {
    max-height: 400px;
    overflow-y: auto;
}

.tournament-list-item {
    padding: 1rem;
    border-bottom: 1px solid #e0e0e0;
    transition: background-color 0.2s;
}

.tournament-list-item:hover {
    background: #f8f9fa;
}

.tournament-list-item:last-child {
    border-bottom: none;
}

.tournament-name-small {
    font-weight: 600;
    color: #2c5530;
    margin-bottom: 0.25rem;
}

.tournament-meta {
    font-size: 0.9rem;
    color: #666;
}

.course-details h3 {
    color: #2c5530;
    margin-bottom: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e0e0e0;
}
</style>
`;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Add modal styles to head
    document.head.insertAdjacentHTML('beforeend', courseModalStyles);
    
    // Initialize courses manager
    window.coursesManager = new CoursesManager();
});